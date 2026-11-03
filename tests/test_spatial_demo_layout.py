from __future__ import annotations

import importlib.util
from pathlib import Path

from beamerpkg.spatial_model import validate_layout

_spec = importlib.util.spec_from_file_location(
    "demo_spatial_layout",
    Path(__file__).resolve().parents[1] / "tools/demo_spatial_layout.py",
)
assert _spec and _spec.loader
demo = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(demo)

SOURCE = {"pdf_path": "demo.pdf", "pdf_sha256": "b" * 64}
PAGE = {
    "width": 453.543,
    "height": 255.118,
    "rotation": 0,
    "box": [0, 0, 453.543, 255.118],
}


def test_demo_layout_is_valid_for_the_demo_page_inventory() -> None:
    layout = demo.demo_layout(SOURCE)
    assert validate_layout(layout, SOURCE, [PAGE] * demo.PAGES) == layout
    # Every page belongs to exactly one frame, in Beamer order.
    pages = [p for _, group in demo.FRAMES for p in group]
    assert pages == list(range(demo.PAGES))


def test_demo_canvas_objects_do_not_overlap() -> None:
    boxes = [(x, y, x + w, y + w * 9 / 16) for x, y, w in demo.PLACES.values()]
    for i, a in enumerate(boxes):
        for b in boxes[i + 1 :]:
            assert a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1]


def test_demo_paths_cover_tour_and_full_deck() -> None:
    layout = demo.demo_layout(SOURCE)
    tour, deck, backup = layout["paths"]
    assert tour["steps"][0]["viewpoint_id"] == "title"
    assert tour["steps"][-1]["viewpoint_id"] == "canvas"
    assert [s["viewpoint_id"] for s in deck["steps"]] == [n for n, _ in demo.FRAMES]
    # The guided talk never enters the backup material; the backup path does.
    appendix = {n for _, names in demo.BACKUP for n in names}
    assert not appendix & {s["viewpoint_id"] for s in tour["steps"]}
    assert [s["viewpoint_id"] for s in backup["steps"]][:2] == [
        "backup",
        "backup-physics",
    ]


def _box(name: str) -> tuple[float, float, float, float]:
    x, y, w = demo.PLACES[name]
    return x, y, x + w, y + w * 9 / 16


def _gap(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    dx = max(b[0] - a[2], a[0] - b[2], 0)
    dy = max(b[1] - a[3], a[1] - b[3], 0)
    return (dx * dx + dy * dy) ** 0.5


def test_demo_backup_parts_are_tight_clusters_apart_from_the_talk() -> None:
    talk = [n for n, _ in demo.FRAMES]
    for _, names in demo.BACKUP:
        inside = [_box(n) for n in names]
        outside = [_box(n) for n in talk if n not in names]
        # Each frame touches its part within one small gap ...
        widest = max(min(_gap(a, b) for b in inside if b is not a) for a in inside)
        # ... and every other frame is far further away than that.
        nearest = min(_gap(a, b) for a in inside for b in outside)
        assert nearest > 8 * widest
    # The whole backup band lies below the talk.
    appendix = {n for _, names in demo.BACKUP for n in names}
    talk_bottom = max(_box(n)[3] for n in demo.PLACES if n not in appendix)
    assert min(_box(n)[1] for n in appendix) > talk_bottom


def test_demo_backup_views_enclose_their_parts() -> None:
    layout = demo.demo_layout(SOURCE)
    views = {v["id"]: v["target"] for v in layout["viewpoints"]}
    for view, names in demo.BACKUP:
        x, y, w, h = views[view]["rect"]
        for n in names:
            b = _box(n)
            assert x <= b[0] and y <= b[1] and b[2] <= x + w and b[3] <= y + h
