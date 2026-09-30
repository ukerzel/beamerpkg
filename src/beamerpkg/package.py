"""Create, validate, and extract beamerpkg containers."""

from __future__ import annotations

import hashlib
import json
import shutil
import stat
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

from .pdf_media import PdfMediaError, discover_pdf_media_references

SCHEMA_VERSION = 1
MANIFEST_NAME = "manifest.json"
ASSET_LIST_SUFFIX = ".beamerpkg-assets"
PACKAGE_SUFFIX = ".beamerpkg"
SOURCE_PREFIX = PurePosixPath("source")


class PackageError(ValueError):
    """Raised when a package or requested asset is invalid."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _file_record(path: Path, archive_path: str) -> dict[str, Any]:
    return {
        "path": archive_path,
        "size": path.stat().st_size,
        "sha256": _sha256(path),
    }


def _safe_relative_path(raw: str) -> PurePosixPath:
    normalized = raw.strip().replace("\\", "/")
    if not normalized:
        raise PackageError("asset path is empty")
    if "://" in normalized or normalized.lower().startswith("file:"):
        raise PackageError(f"remote or URI media references are unsupported: {raw!r}")
    path = PurePosixPath(normalized)
    if path.is_absolute() or ".." in path.parts or "." in path.parts:
        raise PackageError(f"asset path must be a clean relative path: {raw!r}")
    if path.parts[0].endswith(":"):
        raise PackageError(f"asset path must not use a drive prefix: {raw!r}")
    return path


def read_asset_list(path: Path) -> tuple[PurePosixPath, ...]:
    """Read one media path per line, ignoring blank lines and comments."""

    if not path.is_file():
        raise PackageError(f"asset list not found: {path}")

    assets: list[PurePosixPath] = []
    seen: set[str] = set()
    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        try:
            asset = _safe_relative_path(stripped)
        except PackageError as exc:
            raise PackageError(f"{path}:{line_number}: {exc}") from exc
        key = asset.as_posix()
        if key not in seen:
            seen.add(key)
            assets.append(asset)
    return tuple(assets)


def _select_asset_paths(
    pdf: Path,
    asset_list: Path | None,
) -> tuple[PurePosixPath, ...]:
    """Choose explicit sidecar assets or discover them from PDF annotations."""

    if asset_list is not None:
        resolved_asset_list = asset_list.resolve()
        asset_paths = read_asset_list(resolved_asset_list)
        if not asset_paths:
            raise PackageError(
                f"asset list contains no media paths: {resolved_asset_list}"
            )
        return asset_paths

    try:
        discovered = tuple(
            _safe_relative_path(reference)
            for reference in discover_pdf_media_references(pdf)
        )
    except PdfMediaError as exc:
        raise PackageError(str(exc)) from exc

    if discovered:
        return discovered

    legacy_sidecar = pdf.with_suffix(ASSET_LIST_SUFFIX)
    if legacy_sidecar.is_file():
        asset_paths = read_asset_list(legacy_sidecar)
        if asset_paths:
            return asset_paths

    raise PackageError(
        "no supported external media references found in PDF and no "
        f"legacy asset list found at {legacy_sidecar}"
    )


def _collect_source_files(
    source_root: Path,
    source_inputs: tuple[Path, ...],
    output: Path,
) -> tuple[tuple[PurePosixPath, Path], ...]:
    """Collect an explicit editable-source snapshot under the source/ prefix."""

    if not source_inputs:
        return ()

    source_root = source_root.resolve()
    if not source_root.is_dir():
        raise PackageError(f"source root is not a directory: {source_root}")

    output = output.resolve()
    collected: dict[str, tuple[PurePosixPath, Path]] = {}

    def add_file(candidate: Path) -> None:
        if candidate.is_symlink():
            raise PackageError(f"source symlinks are not supported: {candidate}")

        resolved = candidate.resolve()
        try:
            relative = resolved.relative_to(source_root)
        except ValueError as exc:
            raise PackageError(f"source escapes source root: {candidate}") from exc

        if resolved == output:
            raise PackageError(
                "source selection includes the output package; choose narrower "
                f"--source inputs: {candidate}"
            )

        archive_path = SOURCE_PREFIX.joinpath(*relative.parts)
        archive_name = archive_path.as_posix()
        collected[archive_name] = (archive_path, resolved)

    for raw_input in source_inputs:
        if raw_input.is_absolute():
            raise PackageError(f"source input must be relative: {raw_input}")

        relative_input = _safe_relative_path(raw_input.as_posix())
        candidate = source_root.joinpath(*relative_input.parts)

        if not candidate.exists():
            raise PackageError(f"source input not found: {raw_input}")
        if candidate.is_symlink():
            raise PackageError(f"source symlinks are not supported: {raw_input}")

        if candidate.is_file():
            add_file(candidate)
            continue
        if not candidate.is_dir():
            raise PackageError(f"source input is not a file or directory: {raw_input}")

        for child in sorted(candidate.rglob("*")):
            if child.is_symlink():
                raise PackageError(f"source symlinks are not supported: {child}")
            if child.is_file():
                add_file(child)

    return tuple(collected[key] for key in sorted(collected))


def pack_package(
    pdf: Path,
    *,
    root: Path | None = None,
    asset_list: Path | None = None,
    output: Path | None = None,
    notes: Path | None = None,
    source_root: Path | None = None,
    sources: tuple[Path, ...] = (),
) -> Path:
    """Bundle a PDF and its declared media files into one relocatable ZIP container."""

    pdf = pdf.resolve()
    if not pdf.is_file():
        raise PackageError(f"presentation PDF not found: {pdf}")
    if pdf.suffix.lower() != ".pdf":
        raise PackageError(f"presentation must be a PDF: {pdf}")

    root = (root or pdf.parent).resolve()
    if not root.is_dir():
        raise PackageError(f"asset root is not a directory: {root}")

    output = (output or pdf.with_suffix(PACKAGE_SUFFIX)).resolve()
    asset_paths = _select_asset_paths(pdf, asset_list)
    resolved_source_root = (source_root or root).resolve()
    source_files = _collect_source_files(resolved_source_root, sources, output)

    reserved = {MANIFEST_NAME, pdf.name}
    resolved_assets: list[tuple[PurePosixPath, Path]] = []
    for archive_path in asset_paths:
        archive_name = archive_path.as_posix()
        if archive_name in reserved:
            raise PackageError(f"asset path collides with package metadata: {archive_name}")
        source = root.joinpath(*archive_path.parts).resolve()
        try:
            source.relative_to(root)
        except ValueError as exc:
            raise PackageError(f"asset escapes root: {archive_name}") from exc
        if not source.is_file():
            raise PackageError(f"asset not found: {archive_name} (resolved to {source})")
        resolved_assets.append((archive_path, source))

    if notes is None:
        candidate = pdf.with_suffix(".pdfpc")
        notes = candidate if candidate.is_file() else None
    elif not notes.is_file():
        raise PackageError(f"notes file not found: {notes}")

    presentation_record = _file_record(pdf, pdf.name)
    asset_records = [
        _file_record(source, archive_path.as_posix())
        for archive_path, source in resolved_assets
    ]
    notes_record = _file_record(notes, notes.name) if notes is not None else None
    source_records = [
        _file_record(source, archive_path.as_posix())
        for archive_path, source in source_files
    ]
    source_record = (
        {"root": SOURCE_PREFIX.as_posix(), "files": source_records}
        if source_records
        else None
    )

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "presentation": presentation_record,
        "notes": notes_record,
        "assets": asset_records,
        "source": source_record,
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        prefix=f".{output.name}.", suffix=".tmp", dir=output.parent, delete=False
    ) as handle:
        temporary_output = Path(handle.name)

    try:
        # Media and PDFs are already compressed. ZIP_STORED keeps packaging fast and
        # preserves media bytes exactly rather than spending CPU for negligible gain.
        with zipfile.ZipFile(temporary_output, "w", compression=zipfile.ZIP_STORED) as zf:
            zf.writestr(
                MANIFEST_NAME,
                json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            )
            zf.write(pdf, arcname=pdf.name)
            if notes is not None:
                zf.write(notes, arcname=notes.name)
            for archive_path, source in resolved_assets:
                zf.write(source, arcname=archive_path.as_posix())
            for archive_path, source in source_files:
                zf.write(source, arcname=archive_path.as_posix())
        temporary_output.replace(output)
    except Exception:
        temporary_output.unlink(missing_ok=True)
        raise

    return output


def _load_manifest(zf: zipfile.ZipFile) -> dict[str, Any]:
    try:
        raw = zf.read(MANIFEST_NAME)
    except KeyError as exc:
        raise PackageError(f"package is missing {MANIFEST_NAME}") from exc
    try:
        manifest = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PackageError("manifest.json is not valid UTF-8 JSON") from exc
    if not isinstance(manifest, dict):
        raise PackageError("manifest.json must contain a JSON object")
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise PackageError(
            "unsupported schema_version: " f"{manifest.get('schema_version')!r}"
        )
    return manifest


def _manifest_records(manifest: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    presentation = manifest.get("presentation")
    if not isinstance(presentation, dict):
        raise PackageError("manifest.presentation must be an object")
    assets = manifest.get("assets")
    if not isinstance(assets, list):
        raise PackageError("manifest.assets must be a list")
    notes = manifest.get("notes")
    source = manifest.get("source")

    records: list[dict[str, Any]] = [presentation]
    if notes is not None:
        if not isinstance(notes, dict):
            raise PackageError("manifest.notes must be an object or null")
        records.append(notes)
    for asset in assets:
        if not isinstance(asset, dict):
            raise PackageError("manifest asset entries must be objects")
        records.append(asset)

    if source is not None:
        if not isinstance(source, dict):
            raise PackageError("manifest.source must be an object or null")
        if source.get("root") != SOURCE_PREFIX.as_posix():
            raise PackageError("manifest.source.root must be 'source'")
        source_files = source.get("files")
        if not isinstance(source_files, list):
            raise PackageError("manifest.source.files must be a list")
        for source_file in source_files:
            if not isinstance(source_file, dict):
                raise PackageError("manifest source entries must be objects")
            source_path = source_file.get("path")
            if not isinstance(source_path, str):
                raise PackageError("manifest source entry is missing string path")
            safe_source_path = _safe_relative_path(source_path)
            if not safe_source_path.parts or safe_source_path.parts[0] != "source":
                raise PackageError("manifest source paths must be under source/")
            records.append(source_file)

    return tuple(records)


def inspect_package(package: Path) -> dict[str, Any]:
    """Validate a package and return its manifest plus an ``ok`` marker."""

    package = package.resolve()
    if not package.is_file():
        raise PackageError(f"package not found: {package}")

    try:
        with zipfile.ZipFile(package, "r") as zf:
            manifest = _load_manifest(zf)
            names = zf.namelist()
            if len(names) != len(set(names)):
                raise PackageError("package contains duplicate ZIP member names")

            records = _manifest_records(manifest)
            expected = {MANIFEST_NAME}
            for record in records:
                archive_path = record.get("path")
                if not isinstance(archive_path, str):
                    raise PackageError("manifest file record is missing string path")
                safe_path = _safe_relative_path(archive_path).as_posix()
                expected.add(safe_path)
                try:
                    payload = zf.read(safe_path)
                except KeyError as exc:
                    raise PackageError(f"package is missing declared file: {safe_path}") from exc
                if record.get("size") != len(payload):
                    raise PackageError(f"size mismatch for {safe_path}")
                digest = hashlib.sha256(payload).hexdigest()
                if record.get("sha256") != digest:
                    raise PackageError(f"SHA-256 mismatch for {safe_path}")

            unexpected = set(names) - expected
            if unexpected:
                raise PackageError(
                    "package contains undeclared files: " + ", ".join(sorted(unexpected))
                )

            presentation_path = manifest["presentation"]["path"]
            if not zf.read(presentation_path).startswith(b"%PDF-"):
                raise PackageError("declared presentation does not look like a PDF")
    except zipfile.BadZipFile as exc:
        raise PackageError(f"not a valid ZIP package: {package}") from exc

    return {"ok": True, "manifest": manifest}


def _is_zip_symlink(info: zipfile.ZipInfo) -> bool:
    mode = info.external_attr >> 16
    return stat.S_ISLNK(mode)


def extract_package(package: Path, destination: Path) -> dict[str, Any]:
    """Validate and safely extract a package into an existing directory."""

    report = inspect_package(package)
    destination = destination.resolve()
    destination.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(package, "r") as zf:
        for info in zf.infolist():
            if _is_zip_symlink(info):
                raise PackageError(f"ZIP symlink entries are not allowed: {info.filename}")
            archive_path = _safe_relative_path(info.filename)
            target = destination.joinpath(*archive_path.parts).resolve()
            try:
                target.relative_to(destination)
            except ValueError as exc:
                raise PackageError(f"ZIP member escapes destination: {info.filename}") from exc
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info, "r") as source, target.open("wb") as sink:
                shutil.copyfileobj(source, sink)

    return report
