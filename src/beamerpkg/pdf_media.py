"""Discover external media references from PDF annotations."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from pypdf import PdfReader
from pypdf.generic import BooleanObject


class PdfMediaError(ValueError):
    """Raised when PDF media annotations cannot be inspected."""


def _resolve(value: Any) -> Any:
    get_object = getattr(value, "get_object", None)
    return get_object() if callable(get_object) else value


def _file_spec_text(value: Any) -> str | None:
    value = _resolve(value)
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        for key in ("/UF", "/F"):
            candidate = _resolve(value.get(key))
            if isinstance(candidate, str):
                return candidate
    return None


def _pdfpc_launch_media_reference(raw: str) -> str | None:
    """Return a media path from a recognized pdfpc launch-link target."""

    reference, separator, query = raw.strip().partition("?")
    if not separator:
        return None

    option_names = {
        part.split("=", 1)[0].strip().lower()
        for part in query.split("&")
        if part.strip()
    }
    if not option_names.intersection({"autostart", "loop", "start", "stop"}):
        return None
    return reference


def discover_pdf_media_references(pdf: Path) -> tuple[str, ...]:
    """Return external media paths referenced by supported PDF annotations.

    Supports standard /Movie annotations emitted by Beamer's multimedia package
    and pdfpc-style /Launch links carrying recognized media options such as
    autostart or loop.
    """

    try:
        reader = PdfReader(str(pdf), strict=False)
    except Exception as exc:
        raise PdfMediaError(
            f"failed to read PDF annotations from {pdf}: {exc}"
        ) from exc

    references: list[str] = []
    seen: set[str] = set()

    try:
        for page in reader.pages:
            annotations = _resolve(page.get("/Annots")) or []
            for annotation_ref in annotations:
                annotation = _resolve(annotation_ref)
                if not isinstance(annotation, dict):
                    continue

                reference: str | None = None
                subtype = annotation.get("/Subtype")

                if subtype == "/Movie":
                    movie = _resolve(annotation.get("/Movie"))
                    if isinstance(movie, dict):
                        reference = _file_spec_text(movie.get("/F"))
                elif subtype == "/Link":
                    action = _resolve(annotation.get("/A"))
                    if isinstance(action, dict) and action.get("/S") == "/Launch":
                        raw = _file_spec_text(action.get("/F"))
                        if raw is not None:
                            reference = _pdfpc_launch_media_reference(raw)

                if reference is None:
                    continue

                key = reference.strip()
                if key and key not in seen:
                    seen.add(key)
                    references.append(key)
    except Exception as exc:
        raise PdfMediaError(
            f"failed to read PDF annotations from {pdf}: {exc}"
        ) from exc

    return tuple(references)


@dataclass(frozen=True)
class MediaPlacement:
    """One annotation, deliberately not deduplicated by asset path."""

    page_index: int
    annotation_index: int
    asset_path: str
    rect_pdf: tuple[float, float, float, float]
    kind: str
    autostart: bool | None
    loop: bool | None
    controls: bool | None


def _placement_path(raw: str, allowed: set[str]) -> str:
    # Match pack's harmless relative-path normalization. The PDF keeps its
    # original reference; both routes restore the same canonical asset path.
    path = raw.strip().replace("\\", "/")
    relative = PurePosixPath(path)
    if (
        not relative.parts
        or relative.is_absolute()
        or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", path)
        or ".." in relative.parts
        or any(ord(c) < 32 for c in path)
    ):
        raise PdfMediaError("unsafe spatial media path")
    path = relative.as_posix()
    if path not in allowed:
        raise PdfMediaError("spatial media path is absent from validated manifest")
    return path


def discover_pdf_media_placements(
    pdf: Path, allowed_assets: set[str]
) -> tuple[MediaPlacement, ...]:
    """Inspect supported local placements without executing PDF actions.

    The caller supplies paths from the already validated manifest. Unknown flags
    remain None; unsupported encoded playback semantics fail visibly.
    """
    placements: list[MediaPlacement] = []
    try:
        reader = PdfReader(str(pdf), strict=False)
        for page_index, page in enumerate(reader.pages):
            for annotation_index, reference in enumerate(
                _resolve(page.get("/Annots")) or []
            ):
                annotation = _resolve(reference)
                if not isinstance(annotation, dict):
                    continue
                kind = "movie"
                autoplay = loop = controls = None
                raw: str | None = None
                action = _resolve(annotation.get("/A"))
                if annotation.get("/Subtype") == "/Movie":
                    movie = _resolve(annotation.get("/Movie"))
                    if not isinstance(movie, dict):
                        raise PdfMediaError("invalid movie dictionary")
                    raw = _file_spec_text(movie.get("/F"))
                    if action is not None and not isinstance(action, dict):
                        raise PdfMediaError("unsupported movie activation options")
                    if isinstance(action, dict):
                        if set(action) - {"/Mode", "/ShowControls"}:
                            raise PdfMediaError("unsupported movie playback options")
                        mode = action.get("/Mode")
                        if mode is not None:
                            if mode not in ("/Repeat", "/Once"):
                                raise PdfMediaError("unsupported movie playback mode")
                            loop = mode == "/Repeat"
                        value = action.get("/ShowControls")
                        if value is not None:
                            if not isinstance(value, (bool, BooleanObject)):
                                raise PdfMediaError("invalid movie controls option")
                            controls = (
                                value.value
                                if isinstance(value, BooleanObject)
                                else value
                            )
                elif (
                    annotation.get("/Subtype") == "/Link"
                    and isinstance(action, dict)
                    and action.get("/S") == "/Launch"
                ):
                    target = _file_spec_text(action.get("/F"))
                    if target is None or _pdfpc_launch_media_reference(target) is None:
                        continue
                    # Normalize like pack does: outer whitespace and empty
                    # options are ignored; anything else must be supported.
                    raw, _, query = target.strip().partition("?")
                    options = [v for v in query.split("&") if v]
                    if len(set(options)) != len(options) or any(
                        v not in {"autostart", "loop"} for v in options
                    ):
                        raise PdfMediaError("unsupported pdfpc media options")
                    kind = "pdfpc_launch"
                    autoplay = True if "autostart" in options else None
                    loop = True if "loop" in options else None
                else:
                    continue
                if raw is None:
                    raise PdfMediaError("missing movie asset path")
                asset = _placement_path(raw, allowed_assets)
                rect = _resolve(annotation.get("/Rect"))
                if not isinstance(rect, (list, tuple)) or len(rect) != 4:
                    raise PdfMediaError("missing or invalid media rectangle")
                if any(isinstance(v, (bool, BooleanObject, str)) for v in rect):
                    raise PdfMediaError("nonnumeric media rectangle")
                x0, y0, x1, y1 = (float(v) for v in rect)
                if not all(math.isfinite(v) for v in (x0, y0, x1, y1)):
                    raise PdfMediaError("nonfinite media rectangle")
                box, media_box = page.cropbox, page.mediabox
                if min(max(x0, x1), float(box.right), float(media_box.right)) <= max(
                    min(x0, x1), float(box.left), float(media_box.left)
                ) or min(max(y0, y1), float(box.top), float(media_box.top)) <= max(
                    min(y0, y1), float(box.bottom), float(media_box.bottom)
                ):
                    raise PdfMediaError("empty visible media rectangle")
                placements.append(
                    MediaPlacement(
                        page_index,
                        annotation_index,
                        asset,
                        (x0, y0, x1, y1),
                        kind,
                        autoplay,
                        loop,
                        controls,
                    )
                )
    except PdfMediaError:
        raise
    except Exception as exc:
        raise PdfMediaError(f"failed to inspect spatial PDF: {exc}") from exc
    return tuple(placements)
