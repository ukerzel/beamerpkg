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
    tour, deck = layout["paths"]
    assert tour["steps"][0]["viewpoint_id"] == "title"
    assert tour["steps"][-1]["viewpoint_id"] == "canvas"
    assert [s["viewpoint_id"] for s in deck["steps"]] == [n for n, _ in demo.FRAMES]
