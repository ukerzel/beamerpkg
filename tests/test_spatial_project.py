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


@pytest.mark.parametrize("name", ["./file", "../outside", "/absolute"])
def test_archive_admission_rejects_noncanonical_or_escaping_members(
    tmp_path: Path, name: str
) -> None:
    path = tmp_path / "bad.beamerpkg"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(name, b"bytes")
    with pytest.raises(PackageError, match="path"):
        with admitted_archive(path):
            pytest.fail("unsafe archive admitted")


def test_invalid_archive_and_missing_package_have_controlled_admission_errors(
    tmp_path: Path,
) -> None:
    path = tmp_path / "bad.beamerpkg"
    for payload in (None, b"not a ZIP"):
        if payload is not None:
            path.write_bytes(payload)
        with pytest.raises(PackageError, match="admission failed"):
            with admitted_archive(path):
                pytest.fail("invalid archive admitted")


def test_archive_growth_during_copy_is_bounded(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original = bundle(tmp_path)
    limits = replace(Limits(), archive_bytes=original.stat().st_size)
    open_file = Path.open

    def grow_before_open(path, *args, **kwargs):
        if path == original and args == ("rb",):
            with open_file(path, "ab") as stream:
                stream.write(b"extra")
        return open_file(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", grow_before_open)
    with pytest.raises(PackageError, match="archive byte limit"):
        with admitted_archive(original, limits):
            pytest.fail("growing archive admitted")


@pytest.mark.parametrize("kind", ["oversized", "utf8", "json", "directory"])
def test_invalid_sidecars_fail_without_leaking_extracted_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, kind: str
) -> None:
    import tempfile

    temp_root = tmp_path / "private-temp"
    temp_root.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(temp_root))
    original = bundle(tmp_path)
    sidecar = original.with_suffix(".spatial.json")
    if kind == "directory":
        sidecar.mkdir()
    else:
        sidecar.write_bytes(
            {"oversized": b" " * 33, "utf8": b"\xff", "json": b"not JSON"}[kind]
        )
    with pytest.raises(PackageError):
        with load_project(original, replace(Limits(), sidecar_bytes=32)):
            pytest.fail("invalid sidecar admitted")
    assert list(temp_root.iterdir()) == []


@pytest.mark.parametrize("pages", [0, 201])
def test_pdf_page_count_bounds_are_enforced(tmp_path: Path, pages: int) -> None:
    pdf = tmp_path / "talk.pdf"
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=320, height=180)
    writer.write(pdf)
    with pytest.raises(PackageError, match="page limit"):
        with load_project(pack_package(pdf)):
            pytest.fail("out-of-bounds PDF admitted")


@pytest.mark.parametrize("rotation, unit", [(90, 2), (270, 1)])
def test_page_geometry_accounts_for_rotation_and_user_units(
    tmp_path: Path, rotation: int, unit: int
) -> None:
    from pypdf.generic import NameObject, NumberObject

    pdf = tmp_path / "talk.pdf"
    writer = PdfWriter()
    page = writer.add_blank_page(width=320, height=180)
    page.rotate(rotation)
    page[NameObject("/UserUnit")] = NumberObject(unit)
    writer.write(pdf)
    with load_project(pack_package(pdf)) as project:
        geometry = project.data["pages"][0]
        assert geometry["width"] == 180 * unit
        assert geometry["height"] == 320 * unit
        assert geometry["rotation"] == rotation


@pytest.mark.parametrize("kind", ["rotation", "unit", "empty-crop"])
def test_invalid_page_geometry_is_rejected(tmp_path: Path, kind: str) -> None:
    from pypdf.generic import NameObject, NumberObject

    pdf = tmp_path / "talk.pdf"
    writer = PdfWriter()
    page = writer.add_blank_page(width=320, height=180)
    if kind == "rotation":
        page[NameObject("/Rotate")] = NumberObject(45)
    elif kind == "unit":
        page[NameObject("/UserUnit")] = NumberObject(0)
    else:
        page.cropbox.lower_left = (400, 200)
        page.cropbox.upper_right = (500, 300)
    writer.write(pdf)
    with pytest.raises(PackageError, match="invalid spatial page geometry"):
        with load_project(pack_package(pdf)):
            pytest.fail("invalid geometry admitted")
