from __future__ import annotations

import http.client
import threading
from pathlib import Path

import pytest

from beamerpkg.spatial_project import SpatialProject
from beamerpkg.spatial_server import make_server


@pytest.fixture
def server(tmp_path: Path):
    static = tmp_path / "static"
    static.mkdir()
    (static / "index.html").write_text("<html>spatial</html>")
    pdf = tmp_path / "talk.pdf"
    pdf.write_bytes(b"%PDF-1.7\n")
    video = tmp_path / "clip.mp4"
    video.write_bytes(b"0123456789")
    unreferenced = tmp_path / "unreferenced.html"
    unreferenced.write_text("<script>throw new Error('not runtime media')</script>")
    (tmp_path / "secret.tex").write_text("not public")
    project = SpatialProject(
        pdf,
        {"media/clip.mp4": video, "unreferenced.html": unreferenced},
        {
            "source": {},
            "pages": [],
            "layout": {},
            "placements": [{"asset_path": "media/clip.mp4"}],
        },
    )
    instance = make_server(project, static)
    worker = threading.Thread(target=instance.serve_forever, daemon=True)
    worker.start()
    yield instance
    instance.shutdown()
    instance.server_close()
    worker.join(timeout=3)


def request(server, path="/runtime/asset-0", method="GET", **headers):
    connection = http.client.HTTPConnection("127.0.0.1", server.server_port)
    connection.request(method, path, headers=headers)
    response = connection.getresponse()
    result = response.status, dict(response.getheaders()), response.read()
    connection.close()
    return result


@pytest.mark.parametrize(
    "raw, expected, body, content_range",
    [
        ("bytes=2-5", 206, b"2345", "bytes 2-5/10"),
        ("bytes=7-", 206, b"789", "bytes 7-9/10"),
        ("bytes=-3", 206, b"789", "bytes 7-9/10"),
        ("bytes=8-50", 206, b"89", "bytes 8-9/10"),
        ("bytes=20-", 416, b"", "bytes */10"),
        ("bytes=-0", 416, b"", "bytes */10"),
        ("bytes=4-1", 416, b"", "bytes */10"),
        ("bytes=1-2,5-6", 416, b"", "bytes */10"),
        ("bytes=-30", 206, b"0123456789", "bytes 0-9/10"),
        ("bytes=-", 416, b"", "bytes */10"),
        ("items=0-1", 416, b"", "bytes */10"),
        ("bytes=" + "9" * 129 + "-", 416, b"", "bytes */10"),
    ],
)
def test_byte_ranges(server, raw, expected, body, content_range):
    status, headers, data = request(server, Range=raw)
    assert (status, data) == (expected, body)
    assert headers["Content-Range"] == content_range
    assert int(headers["Content-Length"]) == len(body)


def test_head_and_read_only_allowlist(server):
    status, headers, body = request(server, method="HEAD", Range="bytes=2-5")
    assert status == 206 and body == b"" and headers["Content-Length"] == "4"
    assert request(server, method="PUT")[0] == 405
    for path in (
        "/../secret.tex",
        "/%2e%2e/secret.tex",
        "/source/secret.tex",
        "/runtime/missing",
        "/api/spatial",
        "/static/",
    ):
        assert request(server, path)[0] == 404
    status, headers, body = request(server, "/")
    assert status == 200 and body == b"<html>spatial</html>"
    assert "Content-Security-Policy" in headers
    assert "Access-Control-Allow-Origin" not in headers


def test_host_origin_denial_and_no_os_paths(server):
    assert request(server, Host="evil.example")[0] == 403
    assert request(server, Origin="https://evil.example")[0] == 403
    assert request(server, Origin="null")[0] == 403
    status, _, body = request(server, "/api/project")
    assert status == 200
    assert b"/runtime/asset-0" in body and b"/tmp/" not in body


def test_unreferenced_manifest_asset_is_not_browser_surface(server):
    assert request(server, "/runtime/asset-1")[0] == 404


def test_allowlisted_static_symlink_replacement_denied(server, tmp_path: Path):
    index = tmp_path / "static/index.html"
    index.unlink()
    index.symlink_to(tmp_path / "secret.tex")
    assert request(server, "/")[0] == 404


def test_referenced_nonmedia_payload_cannot_be_served_as_executable_html(
    tmp_path: Path,
):
    static = tmp_path / "static"
    static.mkdir()
    (static / "index.html").write_text("viewer")
    pdf = tmp_path / "talk.pdf"
    pdf.write_bytes(b"%PDF-1.7")
    payload = tmp_path / "clip.html"
    payload.write_text("<script>alert('not video')</script>")
    project = SpatialProject(
        pdf, {"clip.html": payload}, {"placements": [{"asset_path": "clip.html"}]}
    )
    instance = make_server(project, static)
    worker = threading.Thread(target=instance.serve_forever, daemon=True)
    worker.start()
    try:
        status, headers, _ = request(instance)
        assert status == 200
        assert headers["Content-Type"] == "application/octet-stream"
        assert headers["Content-Disposition"] == "attachment"
        assert headers["X-Content-Type-Options"] == "nosniff"
    finally:
        instance.shutdown()
        instance.server_close()
        worker.join(timeout=3)


def test_runtime_files_are_served_when_the_temp_dir_is_a_symlink(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # macOS: /var -> /private/var. Boundaries must compare resolved paths.
    import tempfile

    from pypdf import PdfWriter

    from beamerpkg.package import pack_package
    from beamerpkg.spatial_project import load_project

    real = tmp_path / "real"
    real.mkdir()
    (tmp_path / "link").symlink_to(real)
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path / "link"))
    static = tmp_path / "static"
    static.mkdir()
    (static / "index.html").write_text("<html>spatial</html>")
    pdf = tmp_path / "talk.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=320, height=180)
    writer.write(pdf)
    with load_project(pack_package(pdf, root=tmp_path)) as project:
        instance = make_server(project, static)
        worker = threading.Thread(target=instance.serve_forever, daemon=True)
        worker.start()
        try:
            status, _, body = request(
                instance,
                "/runtime/document.pdf",
                Host=f"127.0.0.1:{instance.server_port}",
            )
        finally:
            instance.shutdown()
            instance.server_close()
            worker.join(timeout=3)
    assert status == 200 and body.startswith(b"%PDF")


@pytest.mark.parametrize("method", ["POST", "DELETE", "PATCH", "OPTIONS"])
def test_all_mutation_methods_are_rejected(server, method):
    status, headers, body = request(server, method=method)
    assert status == 405 and body == b""
    assert headers["Allow"] == "GET, HEAD"


def test_absolute_targets_invalid_encoding_and_removed_files_are_not_served(
    server, tmp_path: Path
):
    for target in ("http://127.0.0.1/", "/%ff", "http://[invalid/"):
        assert request(server, target, Host=f"127.0.0.1:{server.server_port}")[0] == 404
    (tmp_path / "clip.mp4").unlink()
    assert request(server)[0] == 404


def test_head_project_and_empty_file_ranges(server, tmp_path: Path):
    status, headers, body = request(server, "/api/project", method="HEAD")
    assert status == 200 and body == b"" and int(headers["Content-Length"]) > 0
    (tmp_path / "clip.mp4").write_bytes(b"")
    status, headers, body = request(server)
    assert status == 200 and body == b"" and headers["Content-Length"] == "0"
    status, headers, body = request(server, Range="bytes=0-")
    assert status == 416 and headers["Content-Range"] == "bytes */0"


def test_missing_frontend_has_an_actionable_error(tmp_path: Path):
    from beamerpkg.package import PackageError

    project = SpatialProject(tmp_path / "talk.pdf", {}, {"placements": []})
    with pytest.raises(PackageError, match="frontend missing"):
        make_server(project, tmp_path / "missing")
