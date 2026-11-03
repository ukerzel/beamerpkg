from __future__ import annotations

import copy
import json

import pytest

from beamerpkg.package import PackageError
from beamerpkg.spatial_model import default_layout, parse_layout, validate_layout


PAGES = [{"width": 320.0, "height": 180.0, "rotation": 0, "box": [0, 0, 320, 180]}] * 3
SOURCE = {"pdf_path": "talk.pdf", "pdf_sha256": "a" * 64}


def test_default_and_explicit_group() -> None:
    model = default_layout(SOURCE, PAGES)
    assert validate_layout(model, SOURCE, PAGES) == model
    model["frames"][0]["page_indices"] = [0, 1, 2]
    model["frames"] = model["frames"][:1]
    model["objects"] = model["objects"][:1]
    model["viewpoints"] = model["viewpoints"][:1]
    model["paths"][0]["steps"] = model["paths"][0]["steps"][:1]
    assert validate_layout(model, SOURCE, PAGES) == model


@pytest.mark.parametrize(
    "failure",
    [
        "nan",
        "bool",
        "duplicate",
        "reference",
        "region",
        "overlap",
        "unknown",
        "hash",
        "nonconsecutive",
        "index",
        "empty",
    ],
)
def test_layout_rejects_real_contract_failures(failure: str) -> None:
    model = copy.deepcopy(default_layout(SOURCE, PAGES))
    if failure == "nan":
        model["objects"][0]["x"] = float("nan")
    elif failure == "bool":
        model["frames"][0]["page_indices"] = [True]
    elif failure == "duplicate":
        model["objects"][1]["id"] = model["objects"][0]["id"]
    elif failure == "reference":
        model["objects"][0]["frame_id"] = "missing"
    elif failure == "region":
        model["viewpoints"][0]["target"]["region"] = [0.9, 0, 0.2, 1]
    elif failure == "overlap":
        model["frames"][1]["page_indices"] = [0]
    elif failure == "unknown":
        model["url"] = "https://untrusted"
    elif failure == "hash":
        model["source"]["pdf_sha256"] = "b" * 64
    elif failure == "nonconsecutive":
        model["frames"][0]["page_indices"] = [0, 2]
    elif failure == "index":
        model["paths"][0]["steps"][0].update(overlay_policy="fixed", overlay_index=99)
    else:
        model["frames"] = []
    with pytest.raises(PackageError):
        validate_layout(model, SOURCE, PAGES)


def test_json_duplicate_keys_and_nonfinite_values_rejected() -> None:
    for raw in ('{"format":"x","format":"y"}', '{"x":NaN}', "[]"):
        with pytest.raises(PackageError):
            parse_layout(raw)
    assert parse_layout(json.dumps(default_layout(SOURCE, PAGES)))


def test_group_rejects_different_page_geometry() -> None:
    pages = copy.deepcopy(PAGES)
    pages[1] = {**pages[1], "rotation": 90}
    model = default_layout(SOURCE, pages)
    model["frames"][0]["page_indices"] = [0, 1]
    with pytest.raises(PackageError, match="geometry"):
        validate_layout(model, SOURCE, pages)


def test_oversized_integer_in_sidecar_is_a_controlled_validation_error() -> None:
    model = default_layout(SOURCE, PAGES)
    model["objects"][0]["x"] = 10**400
    parsed = parse_layout(json.dumps(model))
    with pytest.raises(PackageError, match="finite bounds"):
        validate_layout(parsed, SOURCE, PAGES)


@pytest.mark.parametrize(
    "path, value, message",
    [
        (("format",), "other", "format/schema"),
        (("schema_version",), True, "format/schema"),
        (("media_overrides",), [{}], "reserved"),
        (("frames", 0, "page_indices"), [], "bounded pages"),
        (("objects", 0), None, "record object"),
        (("objects", 0, "width"), 0, "finite bounds"),
        (("objects", 0, "id"), "bad id", "ID"),
        (("viewpoints", 0, "target"), [], "invalid target"),
        (("viewpoints", 0, "target", "object_id"), "missing", "object reference"),
        (("viewpoints", 0, "target", "kind"), "unsupported", "target kind"),
        (("viewpoints", 0, "target", "region"), [0, 0, 1], "four numbers"),
        (("viewpoints", 0, "padding"), 0.46, "finite bounds"),
        (("paths", 0, "steps", 0, "viewpoint_id"), "missing", "viewpoint reference"),
        (("paths", 0, "steps", 0, "overlay_policy"), "random", "overlay policy"),
        (("paths", 0, "steps", 0, "overlay_index"), 0, "cannot fix overlay"),
    ],
)
def test_layout_rejects_incompatible_records_and_references(
    path, value, message
) -> None:
    model = default_layout(SOURCE, PAGES)
    target = model
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    with pytest.raises(PackageError, match=message):
        validate_layout(model, SOURCE, PAGES)


def test_required_fields_and_collection_limits_are_enforced() -> None:
    model = default_layout(SOURCE, PAGES)
    del model["objects"][0]["width"]
    with pytest.raises(PackageError, match="required"):
        validate_layout(model, SOURCE, PAGES)
    model = default_layout(SOURCE, PAGES)
    model["frames"] *= 201
    with pytest.raises(PackageError, match="collection outside bounds"):
        validate_layout(model, SOURCE, PAGES)
    model = default_layout(SOURCE, PAGES)
    model["paths"] = [
        {
            "id": f"p{i}",
            "steps": [
                {"id": f"s{n}", "viewpoint_id": "v0", "overlay_policy": "all"}
                for n in range(1001)
            ],
        }
        for i in range(2)
    ]
    with pytest.raises(PackageError, match="path step limit"):
        validate_layout(model, SOURCE, PAGES)


def test_world_rectangle_view_has_no_overlay_state() -> None:
    model = default_layout(SOURCE, PAGES)
    model["viewpoints"][0]["target"] = {
        "kind": "world_rect",
        "rect": [-100, -200, 1000, 600],
    }
    step = model["paths"][0]["steps"][0]
    step["overlay_policy"] = "fixed"
    assert validate_layout(model, SOURCE, PAGES) == model
    step["overlay_index"] = 0
    with pytest.raises(PackageError, match="no overlays"):
        validate_layout(model, SOURCE, PAGES)
    del step["overlay_index"]
    step["overlay_policy"] = "all"
    with pytest.raises(PackageError, match="no overlays"):
        validate_layout(model, SOURCE, PAGES)
