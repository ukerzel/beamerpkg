from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

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

    assert (
        cli.main(
            [
                "present",
                str(package),
                "--presenter",
                "pdfpc",
                "--",
                "-w",
                "both",
            ]
        )
        == 0
    )
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


def test_pack_and_inspect_cli_report_sources_notes_and_assets(
    tmp_path: Path, capsys
) -> None:
    import json

    from pypdf import PdfWriter

    pdf = tmp_path / "talk.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=320, height=180)
    writer.write(pdf)
    pdf.with_suffix(".pdfpc").write_text("{}")
    (tmp_path / "clip.mp4").write_bytes(b"video")
    (tmp_path / "talk.tex").write_text("source")
    assets = tmp_path / "assets.txt"
    assets.write_text("clip.mp4")
    assert (
        cli.main(["pack", str(pdf), "--assets", str(assets), "--source", "talk.tex"])
        == 0
    )
    package = capsys.readouterr().out.strip()
    assert cli.main(["inspect", package, "--json"]) == 0
    assert (
        json.loads(capsys.readouterr().out)["source"]["files"][0]["path"]
        == "source/talk.tex"
    )
    assert cli.main(["inspect", package]) == 0
    report = capsys.readouterr().out
    assert (
        "talk.pdfpc" in report and "source files: 1" in report and "clip.mp4" in report
    )


def test_cli_package_errors_have_nonzero_status_and_no_traceback(
    tmp_path: Path, capsys
) -> None:
    assert cli.main(["inspect", str(tmp_path / "missing.beamerpkg")]) == 2
    assert capsys.readouterr().err.startswith("beamerpkg: package not found")


@pytest.mark.parametrize(
    "argv",
    [
        ["texdir", "--", "extra"],
        ["texdir", "--typo"],
        ["present", "talk.beamerpkg", "--typo", "--", "-w", "both"],
    ],
)
def test_cli_rejects_ambiguous_or_unrecognized_arguments(argv, capsys) -> None:
    with pytest.raises(SystemExit) as error:
        cli.main(argv)
    assert error.value.code == 2
    assert "error:" in capsys.readouterr().err


def test_missing_presenter_has_an_actionable_error(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    monkeypatch.setattr(cli.shutil, "which", lambda _: None)
    assert cli.main(["present", str(tmp_path / "talk.beamerpkg")]) == 2
    assert "presenter executable not found: pdfpc" in capsys.readouterr().err


def test_presenter_failure_status_is_preserved_and_extraction_is_removed(
    tmp_path: Path, monkeypatch
) -> None:
    from pypdf import PdfWriter

    pdf = tmp_path / "talk.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=320, height=180)
    writer.write(pdf)
    package = pack_package(pdf)
    observed = []
    monkeypatch.setattr(cli.shutil, "which", lambda _: "/fake/pdfpc")

    def fail(command, *, cwd, check):
        assert (cwd / "talk.pdf").is_file()
        observed.append(cwd)
        return SimpleNamespace(returncode=7)

    monkeypatch.setattr(cli.subprocess, "run", fail)
    assert cli.main(["present", str(package)]) == 7
    assert not observed[0].exists()
