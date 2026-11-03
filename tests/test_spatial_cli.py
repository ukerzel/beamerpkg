from __future__ import annotations

import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

from pypdf import PdfWriter

from beamerpkg import cli, spatial_server
from beamerpkg.package import pack_package


def test_legacy_commands_ignore_invalid_spatial_sidecar_and_never_import_spatial(
    tmp_path: Path,
) -> None:
    pdf = tmp_path / "talk.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=320, height=180)
    writer.write(pdf)
    package = pack_package(pdf)
    package.with_suffix(".spatial.json").write_text("not JSON")
    presenter = tmp_path / "presenter"
    presenter.write_text("#!/bin/sh\nexit 0\n")
    presenter.chmod(0o700)
    code = """import importlib.abc, sys
class BlockSpatial(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.startswith('beamerpkg.spatial'):
            raise AssertionError('legacy route imported spatial')
sys.meta_path.insert(0, BlockSpatial())
from beamerpkg.cli import main
assert main(['inspect', sys.argv[1]]) == 0
assert main(['present', sys.argv[1], '--presenter', sys.argv[2]]) == 0
"""
    result = subprocess.run(
        [sys.executable, "-c", code, str(package), str(presenter)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_spatial_cli_only_dispatches_to_selected_route(
    monkeypatch, tmp_path: Path
) -> None:
    observed = {}

    def run(package, *, open_browser):
        observed.update(package=package, open_browser=open_browser)
        return 0

    monkeypatch.setattr(spatial_server, "run_spatial", run)
    monkeypatch.setattr(
        cli.shutil,
        "which",
        lambda _: (_ for _ in ()).throw(AssertionError("pdfpc queried")),
    )
    package = tmp_path / "talk.beamerpkg"
    assert cli.main(["spatial", str(package), "--no-browser"]) == 0
    assert observed == {"package": package, "open_browser": False}


def test_interrupt_closes_server_before_extracted_files_are_removed(
    monkeypatch, tmp_path: Path
) -> None:
    pdf = tmp_path / "talk.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=320, height=180)
    writer.write(pdf)
    package = pack_package(pdf)
    observed = {}

    def make(project):
        observed["pdf"] = project.pdf

        def serve(**kwargs):
            assert project.pdf.exists()
            raise KeyboardInterrupt

        def close():
            observed["closed_while_alive"] = project.pdf.exists()

        return SimpleNamespace(
            server_port=1234, serve_forever=serve, server_close=close
        )

    monkeypatch.setattr(spatial_server, "make_server", make)
    assert spatial_server.run_spatial(package, open_browser=False) == 0
    assert observed["closed_while_alive"] is True
    assert not observed["pdf"].exists()
    assert pdf.exists() and package.exists()


def test_browser_launch_failure_keeps_manual_url_and_closes_server(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    observed = []

    @contextmanager
    def load(package):
        yield SimpleNamespace()

    def serve(**kwargs):
        raise KeyboardInterrupt

    server = SimpleNamespace(
        server_port=1234,
        serve_forever=serve,
        server_close=lambda: observed.append("closed"),
    )
    monkeypatch.setattr(spatial_server, "load_project", load)
    monkeypatch.setattr(spatial_server, "make_server", lambda _: server)
    monkeypatch.setattr(spatial_server.webbrowser, "open", lambda _: False)
    assert spatial_server.run_spatial(tmp_path / "talk.beamerpkg") == 0
    captured = capsys.readouterr()
    assert "http://127.0.0.1:1234/" in captured.out
    assert "open the displayed local URL manually" in captured.err
    assert observed == ["closed"]
