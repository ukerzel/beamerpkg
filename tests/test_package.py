from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from beamerpkg.package import PackageError, extract_package, inspect_package, pack_package


def _write_project(tmp_path: Path) -> tuple[Path, Path]:
    pdf = tmp_path / "talk.pdf"
    pdf.write_bytes(b"%PDF-1.7\nminimal test payload\n")
    media = tmp_path / "media"
    media.mkdir()
    (media / "clip.mp4").write_bytes(b"fake-mp4-bytes")
    assets = tmp_path / "talk.beamerpkg-assets"
    assets.write_text("media/clip.mp4\n", encoding="utf-8")
    return pdf, assets


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
