"""Bounded spatial admission and read-only project preparation."""

from __future__ import annotations

import math
import stat
import tempfile
import zipfile
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from pypdf import PdfReader
from pypdf.errors import PyPdfError

from .package import PackageError, _safe_relative_path, extract_package
from .pdf_media import PdfMediaError, discover_pdf_media_placements
from .spatial_model import default_layout, parse_layout, validate_layout


@dataclass(frozen=True)
class Limits:
    """Predeclared spatial-only engineering limits; legacy commands unchanged."""

    archive_bytes: int = 512 * 1024**2
    entries: int = 4096
    entry_bytes: int = 256 * 1024**2
    total_bytes: int = 1024**3
    manifest_bytes: int = 1024**2
    ratio: int = 200
    sidecar_bytes: int = 512 * 1024


@contextmanager
def admitted_archive(path: Path, limits: Limits = Limits()) -> Iterator[Path]:
    """Bound actual bytes before eager legacy validation; pin a private copy."""
    try:
        if path.stat().st_size > limits.archive_bytes:
            raise PackageError("spatial archive byte limit exceeded")
        with tempfile.TemporaryDirectory(prefix="beamerpkg-admission-") as tmp:
            copy = Path(tmp) / "admitted.beamerpkg"
            copied = 0
            with path.open("rb") as source, copy.open("xb") as sink:
                while chunk := source.read(1024 * 1024):
                    copied += len(chunk)
                    if copied > limits.archive_bytes:
                        raise PackageError("spatial archive byte limit exceeded")
                    sink.write(chunk)
            with zipfile.ZipFile(copy) as archive:
                entries = archive.infolist()
                if len(entries) > limits.entries:
                    raise PackageError("spatial ZIP entry count limit exceeded")
                names: set[str] = set()
                total = 0
                actual_total = 0
                for entry in entries:
                    safe = _safe_relative_path(entry.filename).as_posix()
                    if safe != entry.filename or safe in names:
                        raise PackageError("spatial ZIP duplicate/noncanonical path")
                    names.add(safe)
                    if stat.S_ISLNK(entry.external_attr >> 16):
                        raise PackageError("spatial ZIP symlink not allowed")
                    maximum = (
                        min(limits.entry_bytes, limits.manifest_bytes)
                        if safe == "manifest.json"
                        else limits.entry_bytes
                    )
                    total += entry.file_size
                    if entry.file_size > maximum or total > limits.total_bytes:
                        raise PackageError("spatial expanded byte limit exceeded")
                    if entry.file_size > max(1, entry.compress_size) * limits.ratio:
                        raise PackageError("spatial compression ratio limit exceeded")
                    actual = 0
                    with archive.open(entry) as handle:
                        while chunk := handle.read(1024 * 1024):
                            actual += len(chunk)
                            actual_total += len(chunk)
                            if actual > maximum or actual_total > limits.total_bytes:
                                raise PackageError(
                                    "spatial actual expanded byte limit exceeded"
                                )
                    if actual != entry.file_size:
                        raise PackageError("spatial expanded size mismatch")
            yield copy
    except (OSError, zipfile.BadZipFile, RuntimeError, NotImplementedError) as exc:
        raise PackageError(f"spatial archive admission failed: {exc}") from exc


@dataclass
class SpatialProject:
    """Extracted runtime files plus browser-safe project data; no write API."""

    pdf: Path
    assets: dict[str, Path]
    data: dict[str, Any]


def _page_geometry(pdf: Path) -> list[dict[str, Any]]:
    """Visible size and rotation of every page, as PDF.js will show it."""
    try:
        reader = PdfReader(pdf)
        if not 0 < len(reader.pages) <= 200:
            raise PackageError("spatial PDF page limit exceeded")
        pages: list[dict[str, Any]] = []
        for page in reader.pages:
            crop, media = page.cropbox, page.mediabox
            box = [
                max(float(crop.left), float(media.left)),
                max(float(crop.bottom), float(media.bottom)),
                min(float(crop.right), float(media.right)),
                min(float(crop.top), float(media.top)),
            ]
            unit = float(page.get("/UserUnit", 1))
            rotation = page.rotation % 360
            width, height = (box[2] - box[0]) * unit, (box[3] - box[1]) * unit
            if (
                rotation not in (0, 90, 180, 270)
                or unit <= 0
                or not all(math.isfinite(v) for v in (*box, width, height, unit))
                or width <= 0
                or height <= 0
            ):
                raise PackageError("invalid spatial page geometry")
            if rotation in (90, 270):
                width, height = height, width
            pages.append(
                {"width": width, "height": height, "rotation": rotation, "box": box}
            )
        return pages
    except PackageError:
        raise
    except Exception as exc:
        # pypdf hands back raw PDF objects, so malformed pages can also raise
        # TypeError, KeyError or AttributeError; report them, not a traceback.
        raise PackageError(f"spatial project failed: {exc}") from exc


@contextmanager
def load_project(package: Path, limits: Limits = Limits()) -> Iterator[SpatialProject]:
    """Prepare a validated project for the lifetime of a local presentation."""
    try:
        with (
            admitted_archive(package, limits) as admitted,
            tempfile.TemporaryDirectory(prefix="beamerpkg-spatial-") as tmp,
        ):
            # Resolve so the server's boundary checks, which compare resolved
            # paths, also hold under a symlinked temp dir (macOS /var).
            root = Path(tmp).resolve()
            manifest = extract_package(admitted, root)["manifest"]
            pdf_record = manifest["presentation"]
            pdf = root / pdf_record["path"]
            source = {
                "pdf_path": pdf_record["path"],
                "pdf_sha256": pdf_record["sha256"],
            }
            pages = _page_geometry(pdf)
            assets = {
                record["path"]: root / record["path"] for record in manifest["assets"]
            }
            placements = [
                asdict(v) for v in discover_pdf_media_placements(pdf, set(assets))
            ]
            if len(placements) > 2000:
                raise PackageError("spatial media placement limit exceeded")
            sidecar = package.with_suffix(".spatial.json")
            layout = default_layout(source, pages)
            authored = sidecar.exists()
            if authored:
                with sidecar.open("rb") as handle:
                    raw = handle.read(limits.sidecar_bytes + 1)
                if len(raw) > limits.sidecar_bytes:
                    raise PackageError("spatial sidecar byte limit exceeded")
                layout = parse_layout(raw.decode("utf-8"))
            validate_layout(layout, source, pages)
            yield SpatialProject(
                pdf,
                assets,
                {
                    "source": source,
                    "pages": pages,
                    "placements": placements,
                    "layout": layout,
                    "authored_layout": authored,
                },
            )
    except PackageError:
        raise
    except (OSError, ValueError, PdfMediaError, PyPdfError) as exc:
        raise PackageError(f"spatial project failed: {exc}") from exc
