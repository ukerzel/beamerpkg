from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest
from pypdf import PdfWriter
from pypdf.generic import (
    ArrayObject,
    DictionaryObject,
    NameObject,
    NumberObject,
    TextStringObject,
)

from beamerpkg.package import PackageError, extract_package, inspect_package, pack_package
from beamerpkg.pdf_media import discover_pdf_media_references


def _write_project(tmp_path: Path) -> tuple[Path, Path]:
    pdf = tmp_path / "talk.pdf"
    pdf.write_bytes(b"%PDF-1.7\nminimal test payload\n")
    media = tmp_path / "media"
    media.mkdir()
    (media / "clip.mp4").write_bytes(b"fake-mp4-bytes")
    assets = tmp_path / "talk.beamerpkg-assets"
    assets.write_text("media/clip.mp4\n", encoding="utf-8")
    return pdf, assets


def _write_annotated_pdf(
    path: Path,
    *,
    movie: str | None = None,
    launch: str | None = None,
) -> None:
    writer = PdfWriter()
    page = writer.add_blank_page(width=320, height=180)
    annotations = ArrayObject()

    if movie is not None:
        annotation = DictionaryObject(
            {
                NameObject("/Type"): NameObject("/Annot"),
                NameObject("/Subtype"): NameObject("/Movie"),
                NameObject("/Rect"): ArrayObject(
                    [NumberObject(0), NumberObject(0), NumberObject(100), NumberObject(50)]
                ),
                NameObject("/Movie"): DictionaryObject(
                    {NameObject("/F"): TextStringObject(movie)}
                ),
            }
        )
        annotations.append(writer._add_object(annotation))

    if launch is not None:
        annotation = DictionaryObject(
            {
                NameObject("/Type"): NameObject("/Annot"),
                NameObject("/Subtype"): NameObject("/Link"),
                NameObject("/Rect"): ArrayObject(
                    [NumberObject(0), NumberObject(60), NumberObject(100), NumberObject(110)]
                ),
                NameObject("/A"): DictionaryObject(
                    {
                        NameObject("/S"): NameObject("/Launch"),
                        NameObject("/F"): TextStringObject(launch),
                    }
                ),
            }
        )
        annotations.append(writer._add_object(annotation))

    if annotations:
        page[NameObject("/Annots")] = annotations

    with path.open("wb") as handle:
        writer.write(handle)


def test_pack_is_relocatable_and_preserves_relative_media_path(tmp_path: Path) -> None:
    pdf, assets = _write_project(tmp_path)

    package = pack_package(pdf, root=tmp_path, asset_list=assets)

    with zipfile.ZipFile(package) as zf:
        assert set(zf.namelist()) == {"manifest.json", "talk.pdf", "media/clip.mp4"}
        manifest = json.loads(zf.read("manifest.json"))
        assert manifest["presentation"]["path"] == "talk.pdf"
        assert manifest["assets"][0]["path"] == "media/clip.mp4"
        assert zf.read("media/clip.mp4") == b"fake-mp4-bytes"

    relocated = tmp_path / "elsewhere" / package.name
    relocated.parent.mkdir()
    relocated.write_bytes(package.read_bytes())
    extracted = tmp_path / "unpacked"
    extract_package(relocated, extracted)
    assert (extracted / "talk.pdf").is_file()
    assert (extracted / "media" / "clip.mp4").read_bytes() == b"fake-mp4-bytes"


def test_pack_discovers_standard_movie_without_sidecar(tmp_path: Path) -> None:
    pdf = tmp_path / "talk.pdf"
    _write_annotated_pdf(pdf, movie="media/clip.mp4")
    media = tmp_path / "media"
    media.mkdir()
    (media / "clip.mp4").write_bytes(b"video")

    package = pack_package(pdf, root=tmp_path)

    with zipfile.ZipFile(package) as zf:
        manifest = json.loads(zf.read("manifest.json"))
        assert [asset["path"] for asset in manifest["assets"]] == ["media/clip.mp4"]
        assert zf.read("media/clip.mp4") == b"video"


def test_discovery_handles_pdfpc_launch_and_deduplicates(tmp_path: Path) -> None:
    pdf = tmp_path / "talk.pdf"
    _write_annotated_pdf(
        pdf,
        movie="media/clip.mp4",
        launch="media/clip.mp4?autostart&loop",
    )

    assert discover_pdf_media_references(pdf) == ("media/clip.mp4",)


def test_pack_uses_legacy_sidecar_when_pdf_has_no_media_annotation(tmp_path: Path) -> None:
    pdf = tmp_path / "talk.pdf"
    _write_annotated_pdf(pdf)
    media = tmp_path / "media"
    media.mkdir()
    (media / "clip.mp4").write_bytes(b"video")
    pdf.with_suffix(".beamerpkg-assets").write_text(
        "media/clip.mp4\n", encoding="utf-8"
    )

    package = pack_package(pdf, root=tmp_path)

    with zipfile.ZipFile(package) as zf:
        assert "media/clip.mp4" in zf.namelist()


def test_discovery_ignores_unrelated_launch_action(tmp_path: Path) -> None:
    pdf = tmp_path / "talk.pdf"
    _write_annotated_pdf(pdf, launch="scripts/tool.exe?open=1")

    assert discover_pdf_media_references(pdf) == ()


def test_pack_rejects_remote_discovered_movie_reference(tmp_path: Path) -> None:
    pdf = tmp_path / "talk.pdf"
    _write_annotated_pdf(pdf, movie="https://example.org/video.mp4")

    with pytest.raises(PackageError, match="remote or URI"):
        pack_package(pdf, root=tmp_path)


def test_pack_rejects_discovered_path_escape(tmp_path: Path) -> None:
    pdf = tmp_path / "talk.pdf"
    _write_annotated_pdf(pdf, launch="../video.mp4?autostart")

    with pytest.raises(PackageError, match="clean relative path"):
        pack_package(pdf, root=tmp_path)


def test_inspect_detects_tampered_asset(tmp_path: Path) -> None:
    pdf, assets = _write_project(tmp_path)
    package = pack_package(pdf, root=tmp_path, asset_list=assets)

    tampered = tmp_path / "tampered.beamerpkg"
    with zipfile.ZipFile(package) as source, zipfile.ZipFile(tampered, "w") as target:
        for info in source.infolist():
            payload = source.read(info.filename)
            if info.filename == "media/clip.mp4":
                payload = b"changed"
            target.writestr(info.filename, payload)

    with pytest.raises(PackageError, match="mismatch"):
        inspect_package(tampered)


def test_pack_rejects_asset_path_escape(tmp_path: Path) -> None:
    pdf, assets = _write_project(tmp_path)
    assets.write_text("../secret.mp4\n", encoding="utf-8")

    with pytest.raises(PackageError, match="clean relative path"):
        pack_package(pdf, root=tmp_path, asset_list=assets)


def test_pack_includes_same_name_pdfpc_sidecar_and_extracts_it(tmp_path: Path) -> None:
    pdf, assets = _write_project(tmp_path)
    notes = tmp_path / "talk.pdfpc"
    notes.write_text(
        json.dumps(
            {
                "pdfpcFormat": 2,
                "disableMarkdown": False,
                "pages": [
                    {
                        "idx": 0,
                        "label": "",
                        "overlay": 0,
                        "note": "Portable speaker note",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    package = pack_package(pdf, root=tmp_path, asset_list=assets)

    report = inspect_package(package)
    assert report["manifest"]["notes"]["path"] == "talk.pdfpc"

    with zipfile.ZipFile(package) as zf:
        assert "talk.pdfpc" in zf.namelist()
        assert json.loads(zf.read("talk.pdfpc"))["pages"][0]["note"] == (
            "Portable speaker note"
        )

    extracted = tmp_path / "unpacked-notes"
    extract_package(package, extracted)
    assert (extracted / "talk.pdfpc").read_text(encoding="utf-8") == (
        notes.read_text(encoding="utf-8")
    )


def test_pack_includes_editable_source_snapshot(tmp_path: Path) -> None:
    runtime_root = tmp_path / "runtime"
    runtime_root.mkdir()
    pdf = runtime_root / "talk.pdf"
    pdf.write_bytes(b"%PDF-1.7\nminimal\n")
    media = runtime_root / "media"
    media.mkdir()
    (media / "clip.mp4").write_bytes(b"video")
    assets = runtime_root / "talk.beamerpkg-assets"
    assets.write_text("media/clip.mp4\n", encoding="utf-8")

    source_root = tmp_path / "authoring"
    (source_root / "figures").mkdir(parents=True)
    (source_root / "talk.tex").write_text(
        "\\documentclass{beamer}\n",
        encoding="utf-8",
    )
    (source_root / "figures" / "plot.png").write_bytes(b"png-bytes")

    package = pack_package(
        pdf,
        root=runtime_root,
        asset_list=assets,
        source_root=source_root,
        sources=(Path("talk.tex"), Path("figures")),
    )

    report = inspect_package(package)
    source = report["manifest"]["source"]
    assert source["root"] == "source"
    assert [record["path"] for record in source["files"]] == [
        "source/figures/plot.png",
        "source/talk.tex",
    ]

    with zipfile.ZipFile(package) as zf:
        assert zf.read("source/talk.tex") == b"\\documentclass{beamer}\n"
        assert zf.read("source/figures/plot.png") == b"png-bytes"

    extracted = tmp_path / "unpacked-source"
    extract_package(package, extracted)
    assert (extracted / "source" / "talk.tex").is_file()
    assert (extracted / "source" / "figures" / "plot.png").read_bytes() == (
        b"png-bytes"
    )


def test_pack_rejects_source_path_escape(tmp_path: Path) -> None:
    pdf, assets = _write_project(tmp_path)
    (tmp_path.parent / "outside.tex").write_text("outside", encoding="utf-8")

    with pytest.raises(PackageError, match="clean relative path"):
        pack_package(
            pdf,
            root=tmp_path,
            asset_list=assets,
            source_root=tmp_path,
            sources=(Path("../outside.tex"),),
        )


def test_pack_rejects_missing_source_input(tmp_path: Path) -> None:
    pdf, assets = _write_project(tmp_path)

    with pytest.raises(PackageError, match="source input not found"):
        pack_package(
            pdf,
            root=tmp_path,
            asset_list=assets,
            source_root=tmp_path,
            sources=(Path("missing.tex"),),
        )
