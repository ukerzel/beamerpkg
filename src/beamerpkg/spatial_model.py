"""Strict, read-only spatial sidecar contract (schema 1)."""

from __future__ import annotations

import json
import math
import re
from typing import Any, NoReturn

from .package import PackageError

ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}\Z")


def _fail(message: str) -> NoReturn:
    raise PackageError("spatial layout: " + message)


def parse_layout(raw: str) -> dict[str, Any]:
    """Parse JSON without duplicate keys or JavaScript numeric extensions."""

    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                _fail("duplicate JSON key")
            result[key] = value
        return result

    def constant(value: str) -> None:
        _fail("nonfinite JSON value: " + value)

    try:
        value = json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)
    except (ValueError, RecursionError) as exc:
        raise PackageError(f"spatial layout: invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        _fail("expected an object")
    return value


def _fields(value: Any, required: set[str], optional: set[str] | None = None) -> None:
    if not isinstance(value, dict) or not required <= value.keys():
        _fail("missing required object fields")
    if value.keys() - required - (optional or set()):
        _fail("unknown fields")


def _number(value: Any, low: float, high: float, *, positive: bool = False) -> None:
    if (
        type(value) not in (int, float)
        or not low <= value <= high
        or not math.isfinite(value)
        or (positive and value <= 0)
    ):
        _fail("number outside finite bounds")


def _records(value: Any, maximum: int, *, empty: bool = False) -> dict[str, Any]:
    if not isinstance(value, list) or len(value) > maximum or (not value and not empty):
        _fail("collection outside bounds")
    records: dict[str, Any] = {}
    for item in value:
        if not isinstance(item, dict):
            _fail("expected record object")
        key = item.get("id")
        if not isinstance(key, str) or not ID.fullmatch(key) or key in records:
            _fail("invalid or duplicate ID")
        records[key] = item
    return records


def _rect(value: Any, *, normalized: bool) -> None:
    if not isinstance(value, list) or len(value) != 4:
        _fail("rectangle needs four numbers")
    for i, number in enumerate(value):
        _number(
            number, 0 if normalized else -1e6, 1 if normalized else 1e6, positive=i >= 2
        )
    if normalized and (value[0] + value[2] > 1 or value[1] + value[3] > 1):
        _fail("region escapes page")


def validate_layout(
    model: dict[str, Any], source: dict[str, Any], pages: list[dict[str, Any]]
) -> dict[str, Any]:
    """Validate structure, binding, geometry and all cross-record references."""
    _fields(
        model,
        {
            "format",
            "schema_version",
            "source",
            "frames",
            "objects",
            "viewpoints",
            "paths",
            "media_overrides",
        },
    )
    if (
        model["format"] != "beamerpkg-spatial"
        or type(model["schema_version"]) is not int
        or model["schema_version"] != 1
    ):
        _fail("unsupported format/schema")
    _fields(model["source"], {"pdf_path", "pdf_sha256"})
    if model["source"] != source:
        _fail("PDF hash/path mismatch; explicit re-import required")
    if model["media_overrides"] != []:
        _fail("media overrides are reserved for a later milestone")
    frames = _records(model["frames"], 200)
    claimed: set[int] = set()
    for frame in frames.values():
        _fields(frame, {"id", "page_indices"})
        indices = frame["page_indices"]
        if not isinstance(indices, list) or not indices or len(indices) > len(pages):
            _fail("frame needs bounded pages")
        for index in indices:
            if type(index) is not int or not 0 <= index < len(pages):
                _fail("invalid page index")
        if any(pages[i] != pages[indices[0]] for i in indices):
            _fail("grouped page geometry differs")
        if indices != list(range(indices[0], indices[0] + len(indices))):
            _fail("frame pages must be consecutive and unique")
        if claimed.intersection(indices):
            _fail("overlapping frame groups")
        claimed.update(indices)
    objects = _records(model["objects"], 400)
    for obj in objects.values():
        _fields(obj, {"id", "frame_id", "x", "y", "width"})
        if not isinstance(obj["frame_id"], str) or obj["frame_id"] not in frames:
            _fail("unknown frame reference")
        _number(obj["x"], -1e6, 1e6)
        _number(obj["y"], -1e6, 1e6)
        _number(obj["width"], 0, 1e5, positive=True)
    viewpoints = _records(model["viewpoints"], 800)
    for view in viewpoints.values():
        _fields(view, {"id", "target"}, {"padding"})
        _number(view.get("padding", 0.06), 0, 0.45)
        target = view["target"]
        if not isinstance(target, dict):
            _fail("invalid target")
        if target.get("kind") == "object":
            _fields(target, {"kind", "object_id", "region"})
            if (
                not isinstance(target["object_id"], str)
                or target["object_id"] not in objects
            ):
                _fail("unknown object reference")
            _rect(target["region"], normalized=True)
        elif target.get("kind") == "world_rect":
            _fields(target, {"kind", "rect"})
            _rect(target["rect"], normalized=False)
        else:
            _fail("unknown target kind")
    paths = _records(model["paths"], 32)
    total_steps = 0
    for path in paths.values():
        _fields(path, {"id", "steps"})
        steps = _records(path["steps"], 2000)
        total_steps += len(steps)
        for step in steps.values():
            _fields(step, {"id", "viewpoint_id", "overlay_policy"}, {"overlay_index"})
            if (
                not isinstance(step["viewpoint_id"], str)
                or step["viewpoint_id"] not in viewpoints
            ):
                _fail("unknown viewpoint reference")
            if step["overlay_policy"] not in ("all", "fixed"):
                _fail("unknown overlay policy")
            target = viewpoints[step["viewpoint_id"]]["target"]
            if target["kind"] == "world_rect":
                if step["overlay_policy"] != "fixed" or "overlay_index" in step:
                    _fail("world target has no overlays")
            else:
                frame = frames[objects[target["object_id"]]["frame_id"]]
                index = step.get("overlay_index", 0)
                if type(index) is not int or not 0 <= index < len(
                    frame["page_indices"]
                ):
                    _fail("overlay index outside frame")
                if "overlay_index" in step and step["overlay_policy"] != "fixed":
                    _fail("all policy cannot fix overlay")
    if total_steps > 2000:
        _fail("path step limit exceeded")
    return model


def default_layout(
    source: dict[str, Any], pages: list[dict[str, Any]]
) -> dict[str, Any]:
    """One page per frame; no inferred Beamer overlay grouping."""
    return {
        "format": "beamerpkg-spatial",
        "schema_version": 1,
        "source": source,
        "frames": [{"id": f"f{i}", "page_indices": [i]} for i in range(len(pages))],
        "objects": [
            {
                "id": f"o{i}",
                "frame_id": f"f{i}",
                "x": (i % 5) * 1120,
                "y": (i // 5) * 800,
                "width": 960,
            }
            for i in range(len(pages))
        ],
        "viewpoints": [
            {
                "id": f"v{i}",
                "target": {
                    "kind": "object",
                    "object_id": f"o{i}",
                    "region": [0, 0, 1, 1],
                },
            }
            for i in range(len(pages))
        ],
        "paths": [
            {
                "id": "main",
                "steps": [
                    {"id": f"s{i}", "viewpoint_id": f"v{i}", "overlay_policy": "all"}
                    for i in range(len(pages))
                ],
            }
        ],
        "media_overrides": [],
    }
