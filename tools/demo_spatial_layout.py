"""Write the authored spatial layout for the pdfpc demo talk (examples/demo.tex).

The same ``demo.beamerpkg`` serves both routes: ``beamerpkg present`` uses pdfpc
and ignores this file; ``beamerpkg spatial`` reads it from beside the archive.
A layout is bound to the exact PDF bytes (SHA-256), and pdflatex output differs
per build, so the sidecar is generated after each build instead of committed.

Canvas: the title is the hub; the talk's four acts sit around it clockwise
(problem left, Beamer top, media right, shipping bottom). Two pdfpc-specific
frames (page transitions, presenter screen) are small satellites off the tour
but stay on the canvas and in the ``deck`` path, which keeps the original order.

Backup material (the frames after ``\appendix``) lies in a band below the
main track, away from the tour: each backup part is a tight 2x2 cluster of its
divider and three frames, so gaps inside a part are much smaller than gaps
between parts or to the talk. Each part has a world-rectangle viewpoint for
jumping there during questions, and the ``backup`` path visits them in order.

Usage: python tools/demo_spatial_layout.py examples/demo.beamerpkg
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Physical PDF pages (zero-based) of each Beamer frame in examples/demo.tex.
FRAMES: list[tuple[str, list[int]]] = [
    ("title", [0]),
    ("folder", [1, 2, 3]),
    ("pipeline", [4, 5, 6, 7]),
    ("beamer", [8, 9, 10, 11, 12]),
    ("transitions", [13]),
    ("overlays", [14, 15, 16]),
    ("movie", [17]),
    ("autoplay", [18]),
    ("screens", [19]),
    ("inside", [20, 21, 22, 23, 24]),
    ("try", [25]),
]
# Backup parts: (cluster viewpoint, [divider, frame, frame, frame]); after
# \appendix every backup frame is a single page.
BACKUP: list[tuple[str, list[str]]] = [
    ("backup-physics", ["backup-a", "a-potential", "a-expansion", "a-numbers"]),
    ("backup-container", ["backup-b", "b-manifest", "b-checks", "b-paths"]),
    ("backup-canvas", ["backup-c", "c-sidecar", "c-flight", "c-budget"]),
]
FRAMES += [
    (name, [26 + 4 * part + i])
    for part, (_, names) in enumerate(BACKUP)
    for i, name in enumerate(names)
]
PAGES = 38

# Canvas placement (x, y, width) in world units; 16:9 pages, so height = 0.5625 w.
PLACES: dict[str, tuple[float, float, float]] = {
    "title": (-800, -450, 1600),
    "folder": (-2200, 80, 960),
    "pipeline": (-2200, -620, 960),
    "beamer": (-640, -1400, 1280),
    "transitions": (-1180, -1180, 440),
    "overlays": (780, -1260, 760),
    "movie": (1240, -620, 960),
    "autoplay": (1240, 80, 960),
    "screens": (2340, 160, 520),
    "inside": (80, 780, 960),
    "try": (-1040, 780, 960),
}

# Backup band: cells smaller than talk frames, packed with a small gap inside
# a part and a wide one between parts; the band sits well below the talk.
CELL, CELL_GAP, PART_GAP, BAND_GAP = 560, 28, 360, 560


def _backup_places(talk: dict[str, tuple[float, float, float]]) -> dict[str, Any]:
    """Centre the band under the talk; each part reads divider, then Z order."""
    bottom = max(y + w * 9 / 16 for _, y, w in talk.values())
    centre = (
        min(x for x, _, _ in talk.values()) + max(x + w for x, _, w in talk.values())
    ) / 2
    part_width = 2 * CELL + CELL_GAP
    left = centre - (len(BACKUP) * part_width + (len(BACKUP) - 1) * PART_GAP) / 2
    return {
        name: (
            left + part * (part_width + PART_GAP) + (i % 2) * (CELL + CELL_GAP),
            bottom + BAND_GAP + (i // 2) * (CELL * 9 / 16 + CELL_GAP),
            CELL,
        )
        for part, (_, names) in enumerate(BACKUP)
        for i, name in enumerate(names)
    }


PLACES.update(_backup_places(PLACES))

# Detail regions (normalized to the frame) measured from the rendered pages,
# with fit padding. Equal normalized width/height matches a 16:9 screen; the
# Higgs region runs to the frame edge, so it fits without padding.
DETAILS: dict[str, tuple[str, list[float], float]] = {
    "lagrangian": ("beamer", [0.03, 0.27, 0.47, 0.45], 0.03),
    "higgs": ("beamer", [0.4, 0.2, 0.6, 0.6], 0.0),
    "movie-detail": ("movie", [0.41, 0.28, 0.54, 0.57], 0.03),
}

# Guided tour: (step id, viewpoint, fixed overlay index or None for "all").
TOUR: list[tuple[str, str, int | None]] = [
    ("welcome", "title", None),
    ("problem", "folder", None),
    ("pipeline", "pipeline", None),
    ("beamer", "beamer", 0),
    ("vector-math", "lagrangian", 1),
    ("unstable", "higgs", 2),
    ("vacuum", "higgs", 3),
    ("no-rerender", "beamer", 4),
    ("overlays", "overlays", None),
    ("click-to-play", "movie", None),
    ("in-the-frame", "movie-detail", 0),
    ("autoplay", "autoplay", None),
    ("container", "inside", None),
    ("try-it", "try", None),
    ("everything", "canvas", None),
]


def demo_layout(source: dict[str, str]) -> dict[str, Any]:
    """Return the schema-v1 layout for the demo deck bound to ``source``."""
    aspect = 9 / 16
    boxes = {k: (x, y, w, w * aspect) for k, (x, y, w) in PLACES.items()}
    left = min(b[0] for b in boxes.values())
    top = min(b[1] for b in boxes.values())
    right = max(b[0] + b[2] for b in boxes.values())
    bottom = max(b[1] + b[3] for b in boxes.values())
    viewpoints: list[dict[str, Any]] = [
        {
            "id": name,
            "target": {"kind": "object", "object_id": name, "region": [0, 0, 1, 1]},
        }
        for name, _ in FRAMES
    ]
    viewpoints += [
        {
            "id": view,
            "target": {"kind": "object", "object_id": obj, "region": region},
            "padding": padding,
        }
        for view, (obj, region, padding) in DETAILS.items()
    ]

    def enclosing(names: list[str]) -> list[float]:
        x0 = min(boxes[n][0] for n in names)
        y0 = min(boxes[n][1] for n in names)
        x1 = max(boxes[n][0] + boxes[n][2] for n in names)
        y1 = max(boxes[n][1] + boxes[n][3] for n in names)
        return [x0, y0, x1 - x0, y1 - y0]

    band = [n for _, names in BACKUP for n in names]
    viewpoints.append(
        {"id": "backup", "target": {"kind": "world_rect", "rect": enclosing(band)}}
    )
    viewpoints += [
        {"id": view, "target": {"kind": "world_rect", "rect": enclosing(names)}}
        for view, names in BACKUP
    ]
    viewpoints.append(
        {
            "id": "canvas",
            "target": {
                "kind": "world_rect",
                "rect": [left, top, right - left, bottom - top],
            },
        }
    )

    def step(step_id: str, view: str, overlay: int | None) -> dict[str, Any]:
        if overlay is None:
            fixed = view == "canvas" or view.startswith("backup")
            return {
                "id": step_id,
                "viewpoint_id": view,
                "overlay_policy": "fixed" if fixed else "all",
            }
        return {
            "id": step_id,
            "viewpoint_id": view,
            "overlay_policy": "fixed",
            "overlay_index": overlay,
        }

    return {
        "format": "beamerpkg-spatial",
        "schema_version": 1,
        "source": dict(source),
        "frames": [
            {"id": f"f-{name}", "page_indices": pages} for name, pages in FRAMES
        ],
        "objects": [
            {"id": name, "frame_id": f"f-{name}", "x": x, "y": y, "width": w}
            for name, (x, y, w) in PLACES.items()
        ],
        "viewpoints": viewpoints,
        "paths": [
            {"id": "tour", "steps": [step(*s) for s in TOUR]},
            {
                "id": "deck",
                "steps": [step(f"slide-{name}", name, None) for name, _ in FRAMES],
            },
            {
                "id": "backup",
                "steps": [step("backup", "backup", None)]
                + [
                    step(f"{kind}-{name}", name, None)
                    for view, names in BACKUP
                    for kind, name in [
                        ("part", view),
                        *(("slide", n) for n in names[1:]),
                    ]
                ],
            },
        ],
        "media_overrides": [],
    }


def main(argv: list[str] | None = None) -> int:
    from beamerpkg.package import PackageError
    from beamerpkg.spatial_project import load_project

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("package", type=Path)
    args = parser.parse_args(argv)
    sidecar = args.package.with_suffix(".spatial.json")
    # This generated file is bound to the previous PDF hash; replace it.
    sidecar.unlink(missing_ok=True)
    with load_project(args.package) as project:
        if len(project.data["pages"]) != PAGES:
            print(
                f"demo layout expects {PAGES} pages, found "
                f"{len(project.data['pages'])}; update FRAMES after editing demo.tex",
                file=sys.stderr,
            )
            return 2
        layout = demo_layout(project.data["source"])
    sidecar.write_text(json.dumps(layout, indent=2) + "\n", encoding="utf-8")
    try:
        with load_project(args.package) as project:
            assert project.data["authored_layout"]
    except PackageError:
        sidecar.unlink()
        raise
    print(f"Wrote {sidecar}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
