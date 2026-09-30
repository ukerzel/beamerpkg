"""Discover external media references from PDF annotations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pypdf import PdfReader


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
        raise PdfMediaError(f"failed to read PDF annotations from {pdf}: {exc}") from exc

    references: list[str] = []
    seen: set[str] = set()

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

    return tuple(references)
