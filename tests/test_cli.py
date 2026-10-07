from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from beamerpkg import cli
from beamerpkg.package import pack_package


def test_present_runs_in_extracted_package_root(tmp_path: Path, monkeypatch) -> None:
    pdf = tmp_path / "talk.pdf"
    pdf.write_bytes(b"%PDF-1.7\nminimal\n")
    media = tmp_path / "media"
    media.mkdir()
    (media / "clip.mp4").write_bytes(b"video")
    assets = tmp_path / "talk.beamerpkg-assets"
    assets.write_text("media/clip.mp4\n", encoding="utf-8")
    package = pack_package(pdf, root=tmp_path, asset_list=assets)

    observed: dict[str, object] = {}

    monkeypatch.setattr(cli.shutil, "which", lambda executable: "/usr/bin/pdfpc")

    def fake_run(command, *, cwd, check):
        observed["command"] = command
        observed["cwd"] = cwd
        observed["media_exists"] = (cwd / "media" / "clip.mp4").is_file()
        observed["pdf_exists"] = (cwd / "talk.pdf").is_file()
        observed["check"] = check
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(cli.subprocess, "run", fake_run)

    assert cli.main(["present", str(package)]) == 0
    assert observed["command"] == ["/usr/bin/pdfpc", "talk.pdf"]
    assert observed["media_exists"] is True
    assert observed["pdf_exists"] is True
    assert observed["check"] is False


def test_present_forwards_arguments_after_double_dash(
    tmp_path: Path, monkeypatch
) -> None:
    pdf = tmp_path / "talk.pdf"
    pdf.write_bytes(b"%PDF-1.7\nminimal\n")
    media = tmp_path / "media"
    media.mkdir()
    (media / "clip.mp4").write_bytes(b"video")
    assets = tmp_path / "talk.beamerpkg-assets"
    assets.write_text("media/clip.mp4\n", encoding="utf-8")
    package = pack_package(pdf, root=tmp_path, asset_list=assets)

    observed: dict[str, object] = {}

    monkeypatch.setattr(cli.shutil, "which", lambda executable: "/usr/bin/pdfpc")

    def fake_run(command, *, cwd, check):
        observed["command"] = command
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(cli.subprocess, "run", fake_run)

    assert cli.main(
        [
            "present",
            str(package),
            "--presenter",
            "pdfpc",
            "--",
            "-w",
            "both",
        ]
    ) == 0
    assert observed["command"] == ["/usr/bin/pdfpc", "-w", "both", "talk.pdf"]


def test_present_forwards_unknown_args_when_poetry_strips_separator(
    tmp_path: Path, monkeypatch
) -> None:
    pdf = tmp_path / "talk.pdf"
    pdf.write_bytes(b"%PDF-1.7\nminimal\n")
    media = tmp_path / "media"
    media.mkdir()
    (media / "clip.mp4").write_bytes(b"video")
    assets = tmp_path / "talk.beamerpkg-assets"
    assets.write_text("media/clip.mp4\n", encoding="utf-8")
    package = pack_package(pdf, root=tmp_path, asset_list=assets)

    observed: dict[str, object] = {}

    monkeypatch.setattr(cli.shutil, "which", lambda executable: "/usr/bin/pdfpc")

    def fake_run(command, *, cwd, check):
        observed["command"] = command
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(cli.subprocess, "run", fake_run)

    assert cli.main(["present", str(package), "-w", "both"]) == 0
    assert observed["command"] == ["/usr/bin/pdfpc", "-w", "both", "talk.pdf"]


def test_texdir_prints_directory_with_shipped_latex_helper(capsys) -> None:
    assert cli.main(["texdir"]) == 0

    texdir = Path(capsys.readouterr().out.strip())
    assert texdir.is_absolute()
    assert (texdir / "beamerpkg.sty").is_file()
