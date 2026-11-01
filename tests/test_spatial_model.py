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
