from __future__ import annotations

import hashlib
import json
import stat
import struct
import zipfile
from pathlib import Path
from types import SimpleNamespace

import pytest
from pypdf import PdfWriter
from pypdf.generic import NameObject, NumberObject

from beamerpkg import cli
from beamerpkg.package import (
    PackageError,
    extract_package,
    inspect_package,
    pack_package,
)
from beamerpkg.spatial_project import load_project


def pdf_file(root: Path) -> Path:
    pdf = root / "talk.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=320, height=180)
    writer.write(pdf)
    return pdf


def record(path: str, payload: bytes) -> dict:
    return {
        "path": path,
        "size": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def write_archive(path: Path, manifest: object, files: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("manifest.json", json.dumps(manifest))
        for name, payload in files.items():
            archive.writestr(name, payload)


@pytest.mark.parametrize(
    "input_name", ["talk.pdf", "clip.mp4", "talk.pdfpc", "assets.txt"]
)
def test_pack_cannot_overwrite_an_input(tmp_path: Path, input_name: str) -> None:
    pdf = pdf_file(tmp_path)
    (tmp_path / "clip.mp4").write_bytes(b"video")
    (tmp_path / "talk.pdfpc").write_text("{}")
    assets = tmp_path / "assets.txt"
    assets.write_text("clip.mp4\n")
    output = tmp_path / input_name
    original = output.read_bytes()
    with pytest.raises(PackageError, match="output.*input"):
        pack_package(pdf, asset_list=assets, output=output)
    assert output.read_bytes() == original


def test_explicit_notes_are_restored_under_pdf_stem_on_both_routes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pdf = pdf_file(tmp_path)
    notes = tmp_path / "selected-notes.json"
    notes.write_text('{"pages": []}')
    source = tmp_path / "talk.tex"
    source.write_text("source bytes")
    package = pack_package(pdf, notes=notes, sources=(Path("talk.tex"),))
    relocated = tmp_path / "relocated" / package.name
    relocated.parent.mkdir()
    relocated.write_bytes(package.read_bytes())
    monkeypatch.setattr(cli.shutil, "which", lambda _: "/fake/pdfpc")

    def present(command, *, cwd, check):
        assert command == ["/fake/pdfpc", "talk.pdf"]
        assert (cwd / "talk.pdfpc").read_bytes() == notes.read_bytes()
        assert (cwd / "source/talk.tex").read_bytes() == source.read_bytes()
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(cli.subprocess, "run", present)
    assert cli.main(["present", str(relocated)]) == 0
    with load_project(relocated) as project:
        assert project.pdf.read_bytes() == pdf.read_bytes()
        assert project.pdf.with_suffix(".pdfpc").read_bytes() == notes.read_bytes()


@pytest.mark.parametrize("collision", ["notes", "source", "parent"])
def test_pack_rejects_member_collisions_before_replacing_output(
    tmp_path: Path, collision: str
) -> None:
    pdf = pdf_file(tmp_path)
    (tmp_path / "talk.pdfpc").write_text("{}")
    (tmp_path / "talk.tex").write_text("source")
    asset_root = tmp_path / "assets"
    asset_root.mkdir()
    name = {
        "notes": "talk.pdfpc",
        "source": "source/talk.tex",
        "parent": "talk.pdf/clip.mp4",
    }[collision]
    media = asset_root / name
    media.parent.mkdir(parents=True, exist_ok=True)
    media.write_bytes(b"video")
    assets = tmp_path / "assets.txt"
    assets.write_text(name)
    output = tmp_path / "existing.beamerpkg"
    output.write_bytes(b"previous bundle")
    with pytest.raises(PackageError, match="collid|conflict|duplicate"):
        pack_package(
            pdf,
            root=asset_root,
            asset_list=assets,
            output=output,
            source_root=tmp_path,
            sources=(Path("talk.tex"),),
        )
    assert output.read_bytes() == b"previous bundle"


@pytest.mark.parametrize(
    "raw", [".", "./", "\x00clip.mp4", "https:clip.mp4", "C:clip.mp4"]
)
def test_invalid_asset_paths_fail_with_package_error(tmp_path: Path, raw: str) -> None:
    pdf = pdf_file(tmp_path)
    assets = tmp_path / "assets.txt"
    assets.write_text(raw)
    with pytest.raises(PackageError):
        pack_package(pdf, asset_list=assets)


@pytest.mark.parametrize("path", ["./talk.pdf", " talk.pdf", "talk.pdf/", "talk\\.pdf"])
def test_noncanonical_manifest_paths_fail_cleanly(tmp_path: Path, path: str) -> None:
    pdf = pdf_file(tmp_path)
    package = tmp_path / "bad.beamerpkg"
    manifest = {
        "schema_version": 1,
        "presentation": record(path, pdf.read_bytes()),
        "assets": [],
    }
    write_archive(
        package,
        manifest,
        {
            path.replace("\\", "/")
            .strip()
            .removeprefix("./")
            .rstrip("/"): pdf.read_bytes()
        },
    )
    with pytest.raises(PackageError, match="path"):
        inspect_package(package)


def test_duplicate_manifest_records_and_file_directory_conflicts_are_rejected(
    tmp_path: Path,
) -> None:
    pdf = pdf_file(tmp_path)
    payload = pdf.read_bytes()
    package = tmp_path / "bad.beamerpkg"
    manifest = {
        "schema_version": 1,
        "presentation": record("talk.pdf", payload),
        "assets": [record("talk.pdf", payload)],
    }
    write_archive(package, manifest, {"talk.pdf": payload})
    with pytest.raises(PackageError, match="duplicate|collid"):
        inspect_package(package)
    manifest["assets"] = [record("talk.pdf/clip.mp4", b"video")]
    write_archive(
        package, manifest, {"talk.pdf": payload, "talk.pdf/clip.mp4": b"video"}
    )
    with pytest.raises(PackageError, match="conflict|collid"):
        extract_package(package, tmp_path / "extracted")
    assert not (tmp_path / "extracted/talk.pdf").exists()


def test_inspect_rejects_symlink_members(tmp_path: Path) -> None:
    pdf = pdf_file(tmp_path)
    package = pack_package(pdf)
    bad = tmp_path / "symlink.beamerpkg"
    with zipfile.ZipFile(package) as source, zipfile.ZipFile(bad, "w") as target:
        for info in source.infolist():
            if info.filename == "talk.pdf":
                info.external_attr = (stat.S_IFLNK | 0o777) << 16
            target.writestr(info, source.read(info.filename))
    with pytest.raises(PackageError, match="symlink"):
        inspect_package(bad)


def test_malformed_annotation_has_controlled_pack_error(tmp_path: Path) -> None:
    pdf = tmp_path / "talk.pdf"
    writer = PdfWriter()
    page = writer.add_blank_page(width=320, height=180)
    page[NameObject("/Annots")] = NumberObject(42)
    writer.write(pdf)
    with pytest.raises(PackageError, match="annotations"):
        pack_package(pdf)


@pytest.mark.parametrize(
    "fault",
    [
        "schema-bool",
        "size-bool",
        "size-float",
        "missing",
        "hash",
        "undeclared",
        "source-root",
        "source-file",
        "record-path",
        "assets",
        "presentation",
        "notes",
    ],
)
def test_invalid_manifest_and_payload_contracts(tmp_path: Path, fault: str) -> None:
    payload = b"%PDF-1.7\n"
    manifest = {
        "schema_version": 1,
        "presentation": record("talk.pdf", payload),
        "assets": [],
    }
    files = {"talk.pdf": payload}
    if fault == "schema-bool":
        manifest["schema_version"] = True
    elif fault in {"size-bool", "size-float"}:
        # Booleans compare equal to integers; use a one-byte asset to expose it.
        manifest["assets"] = [record("clip.mp4", b"x")]
        manifest["assets"][0]["size"] = True if fault == "size-bool" else 1.0
        files["clip.mp4"] = b"x"
    elif fault == "missing":
        files.clear()
    elif fault == "hash":
        files["talk.pdf"] = b"%PDF-1.6\n"  # same size, different hash
    elif fault == "undeclared":
        files["secret.txt"] = b"undeclared"
    elif fault == "source-root":
        manifest["source"] = {"root": "other", "files": []}
    elif fault == "source-file":
        manifest["source"] = {"root": "source", "files": [record("talk.pdf", payload)]}
    elif fault == "record-path":
        manifest["presentation"]["path"] = None
    else:
        manifest[fault] = "wrong type"
    package = tmp_path / "bad.beamerpkg"
    write_archive(package, manifest, files)
    with pytest.raises(PackageError):
        inspect_package(package)


@pytest.mark.parametrize(
    "raw", [b"not ZIP", b"\xff", b"[]", b"{", b"[" * 1100 + b"]" * 1100]
)
def test_invalid_archives_and_manifest_json_fail_cleanly(
    tmp_path: Path, raw: bytes
) -> None:
    package = tmp_path / "bad.beamerpkg"
    if raw == b"not ZIP":
        package.write_bytes(raw)
    else:
        with zipfile.ZipFile(package, "w") as archive:
            archive.writestr("manifest.json", raw)
    with pytest.raises(PackageError):
        inspect_package(package)


@pytest.mark.parametrize("fault", ["encryption", "compression"])
def test_unreadable_zip_members_fail_cleanly(tmp_path: Path, fault: str) -> None:
    package = pack_package(pdf_file(tmp_path))
    raw = bytearray(package.read_bytes())
    local = raw.index(b"PK\x03\x04")
    central = raw.index(b"PK\x01\x02")
    if fault == "encryption":
        for offset in (local + 6, central + 8):
            struct.pack_into("<H", raw, offset, 1)
    else:
        for offset in (local + 8, central + 10):
            struct.pack_into("<H", raw, offset, 99)
    package.write_bytes(raw)
    with pytest.raises(PackageError, match="cannot read ZIP"):
        inspect_package(package)


def test_extraction_cannot_follow_a_destination_symlink_outside_root(
    tmp_path: Path,
) -> None:
    pdf = pdf_file(tmp_path)
    (tmp_path / "clip.mp4").write_bytes(b"video")
    assets = tmp_path / "assets.txt"
    assets.write_text("clip.mp4")
    package = pack_package(pdf, asset_list=assets)
    destination = tmp_path / "unpacked"
    destination.mkdir()
    outside = tmp_path / "outside.mp4"
    outside.write_bytes(b"preserve")
    (destination / "clip.mp4").symlink_to(outside)
    with pytest.raises(PackageError, match="escapes destination"):
        extract_package(package, destination)
    assert outside.read_bytes() == b"preserve"


def test_failed_pack_preserves_previous_bundle_and_removes_temporary_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pdf = pdf_file(tmp_path)
    output = tmp_path / "talk.beamerpkg"
    output.write_bytes(b"previous bundle")

    def fail(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(zipfile.ZipFile, "write", fail)
    with pytest.raises(OSError, match="disk full"):
        pack_package(pdf, output=output)
    assert output.read_bytes() == b"previous bundle"
    assert not list(tmp_path.glob(".talk.beamerpkg.*.tmp"))


@pytest.mark.parametrize("kind", ["file", "directory", "nested", "parent"])
def test_source_selection_rejects_symlinks_at_every_depth(
    tmp_path: Path, kind: str
) -> None:
    pdf = pdf_file(tmp_path)
    (tmp_path / "talk.tex").write_text("source")
    (tmp_path / "figures").mkdir()
    (tmp_path / "figures/plot.png").write_bytes(b"figure")
    if kind == "file":
        selected = Path("linked.tex")
        (tmp_path / selected).symlink_to(tmp_path / "talk.tex")
    elif kind in {"directory", "parent"}:
        (tmp_path / "linked").symlink_to(tmp_path / "figures", target_is_directory=True)
        selected = Path("linked") if kind == "directory" else Path("linked/plot.png")
    else:
        selected = Path("figures")
        (tmp_path / "figures/linked.tex").symlink_to(tmp_path / "talk.tex")
    with pytest.raises(PackageError, match="source symlinks"):
        pack_package(pdf, sources=(selected,))
    assert not pdf.with_suffix(".beamerpkg").exists()


def test_source_parent_symlink_cannot_escape_source_root(tmp_path: Path) -> None:
    pdf = pdf_file(tmp_path)
    source_root = tmp_path / "authoring"
    source_root.mkdir()
    (tmp_path / "outside.tex").write_text("private")
    (source_root / "outside").symlink_to(tmp_path, target_is_directory=True)
    with pytest.raises(PackageError, match="symlink|escapes source root"):
        pack_package(
            pdf, source_root=source_root, sources=(Path("outside/outside.tex"),)
        )


@pytest.mark.parametrize("kind", ["absolute", "missing-root", "output"])
def test_invalid_source_selection_preserves_inputs(tmp_path: Path, kind: str) -> None:
    pdf = pdf_file(tmp_path)
    source = tmp_path / "talk.tex"
    source.write_bytes(b"preserve source")
    kwargs = {"sources": (Path("talk.tex"),)}
    if kind == "absolute":
        kwargs["sources"] = (source,)
    elif kind == "missing-root":
        kwargs["source_root"] = tmp_path / "missing"
    else:
        kwargs["output"] = source
    with pytest.raises(PackageError, match="relative|source root|includes the output"):
        pack_package(pdf, **kwargs)
    assert source.read_bytes() == b"preserve source"


@pytest.mark.parametrize(
    "kind",
    [
        "missing-pdf",
        "extension",
        "root",
        "asset",
        "asset-escape",
        "metadata-collision",
        "notes",
        "asset-list",
    ],
)
def test_invalid_pack_inputs_are_rejected_before_output(
    tmp_path: Path, kind: str
) -> None:
    pdf = pdf_file(tmp_path)
    assets = tmp_path / "assets.txt"
    assets.write_text("clip.mp4\n")
    kwargs = {}
    if kind == "missing-pdf":
        pdf.unlink()
    elif kind == "extension":
        renamed = pdf.with_suffix(".txt")
        pdf.rename(renamed)
        pdf = renamed
    elif kind == "root":
        kwargs["root"] = tmp_path / "missing"
    elif kind == "asset":
        kwargs["asset_list"] = assets
    elif kind == "asset-escape":
        asset_root = tmp_path / "media-root"
        asset_root.mkdir()
        (tmp_path / "private.mp4").write_bytes(b"private")
        (asset_root / "clip.mp4").symlink_to(tmp_path / "private.mp4")
        kwargs.update(root=asset_root, asset_list=assets)
    elif kind == "metadata-collision":
        assets.write_text("manifest.json")
        kwargs["asset_list"] = assets
    elif kind == "notes":
        kwargs["notes"] = tmp_path / "missing.pdfpc"
    else:
        kwargs["asset_list"] = tmp_path / "missing.txt"
    with pytest.raises(PackageError):
        pack_package(pdf, **kwargs)
    assert not pdf.with_suffix(".beamerpkg").exists()


def test_asset_list_deduplicates_and_source_selections_can_overlap(
    tmp_path: Path,
) -> None:
    pdf = pdf_file(tmp_path)
    (tmp_path / "clip.mp4").write_bytes(b"video")
    (tmp_path / "sources").mkdir()
    (tmp_path / "sources/talk.tex").write_bytes(b"source")
    assets = tmp_path / "assets.txt"
    assets.write_text("# comment\n\nclip.mp4\nclip.mp4\n")
    package = pack_package(
        pdf, asset_list=assets, sources=(Path("sources"), Path("sources/talk.tex"))
    )
    manifest = inspect_package(package)["manifest"]
    assert len(manifest["assets"]) == 1
    assert [r["path"] for r in manifest["source"]["files"]] == [
        "source/sources/talk.tex"
    ]


@pytest.mark.parametrize(
    "field, value",
    [
        ("source", []),
        ("source", {"root": "source", "files": {}}),
        ("source", {"root": "source", "files": [None]}),
        ("source", {"root": "source", "files": [{"path": 42}]}),
        ("assets", [None]),
    ],
)
def test_malformed_manifest_file_collections_fail_cleanly(
    tmp_path: Path, field, value
) -> None:
    payload = b"%PDF-1.7\n"
    manifest = {
        "schema_version": 1,
        "presentation": record("talk.pdf", payload),
        "assets": [],
        field: value,
    }
    package = tmp_path / "bad.beamerpkg"
    write_archive(package, manifest, {"talk.pdf": payload})
    with pytest.raises(PackageError, match="manifest"):
        inspect_package(package)


def test_missing_manifest_and_non_pdf_presentation_are_rejected(tmp_path: Path) -> None:
    package = tmp_path / "bad.beamerpkg"
    with zipfile.ZipFile(package, "w") as archive:
        archive.writestr("talk.pdf", b"not PDF")
    with pytest.raises(PackageError, match="missing manifest"):
        inspect_package(package)
    write_archive(
        package,
        {
            "schema_version": 1,
            "presentation": record("talk.pdf", b"not PDF"),
            "assets": [],
        },
        {"talk.pdf": b"not PDF"},
    )
    with pytest.raises(PackageError, match="does not look like a PDF"):
        inspect_package(package)
