from __future__ import annotations

import json
import zipfile
from dataclasses import replace
from pathlib import Path

import pytest
from pypdf import PdfWriter

from beamerpkg.package import PackageError, pack_package
from beamerpkg.spatial_project import Limits, admitted_archive, load_project


def bundle(root: Path) -> Path:
    pdf = root / "talk.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=320, height=180)
    writer.write(pdf)
    return pack_package(pdf, root=root)


def test_admitted_copy_survives_source_replacement(tmp_path: Path) -> None:
    original = bundle(tmp_path)
    with admitted_archive(original) as admitted:
        assert admitted != original
        original.write_bytes(b"replacement")
        with zipfile.ZipFile(admitted) as archive:
            assert "talk.pdf" in archive.namelist()
        retained = admitted
    assert not retained.exists()


def test_archive_limits_precede_existing_validator(tmp_path: Path) -> None:
    original = bundle(tmp_path)
    for limits in (
        replace(Limits(), archive_bytes=1),
        replace(Limits(), entry_bytes=1),
        replace(Limits(), total_bytes=1),
        replace(Limits(), entries=1),
        replace(Limits(), manifest_bytes=1),
    ):
        with pytest.raises(PackageError, match="limit"):
            with admitted_archive(original, limits):
                pytest.fail("invalid archive admitted")


def test_compression_bomb_and_symlink_rejected(tmp_path: Path) -> None:
    original = tmp_path / "bad.beamerpkg"
    with zipfile.ZipFile(original, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("huge", b"0" * 100_000)
    with pytest.raises(PackageError, match="ratio"):
        with admitted_archive(original):
            pass
    with zipfile.ZipFile(original, "w") as archive:
        entry = zipfile.ZipInfo("link")
        entry.external_attr = 0o120777 << 16
        archive.writestr(entry, "outside")
    with pytest.raises(PackageError, match="symlink"):
        with admitted_archive(original):
            pass


def test_project_default_and_stale_sidecar(tmp_path: Path) -> None:
    original = bundle(tmp_path)
    with load_project(original) as project:
        assert project.data["layout"]["frames"][0]["page_indices"] == [0]
        assert project.pdf.is_file()
        assert project.data["placements"] == []
        layout = project.data["layout"]
    layout["source"]["pdf_sha256"] = "0" * 64
    original.with_suffix(".spatial.json").write_text(json.dumps(layout))
    with pytest.raises(PackageError, match="hash"):
        with load_project(original):
            pass


def test_malformed_pdf_has_controlled_spatial_error(tmp_path: Path) -> None:
    pdf = tmp_path / "talk.pdf"
    pdf.write_bytes(b"%PDF-1.7\nnot a complete PDF")
    assets = tmp_path / "empty.txt"
    assets.write_text("")
    package = pack_package(pdf, asset_list=assets)
    with pytest.raises(PackageError, match="spatial project failed"):
        with load_project(package):
            pass


def test_page_geometry_uses_visible_crop_media_intersection(tmp_path: Path) -> None:
    pdf = tmp_path / "talk.pdf"
    writer = PdfWriter()
    page = writer.add_blank_page(width=320, height=180)
    page.cropbox.lower_left = (-10, -10)
    page.cropbox.upper_right = (400, 200)
    writer.write(pdf)
    package = pack_package(pdf)
    with load_project(package) as project:
        assert project.data["pages"][0]["box"] == [0, 0, 320, 180]


def test_malformed_page_values_fail_as_package_errors(tmp_path: Path) -> None:
    # pypdf hands back raw objects; a wrong type must not escape as a traceback.
    from pypdf.generic import ArrayObject, NameObject, NumberObject

    pdf = tmp_path / "talk.pdf"
    writer = PdfWriter()
    page = writer.add_blank_page(width=320, height=180)
    page[NameObject("/UserUnit")] = ArrayObject([NumberObject(1)])
    writer.write(pdf)
    with pytest.raises(PackageError, match="spatial project failed"):
        with load_project(pack_package(pdf, root=tmp_path)):
            pytest.fail("malformed page admitted")
