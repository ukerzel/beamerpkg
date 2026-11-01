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
    (tmp_path / "secret.tex").write_text("not public")
    project = SpatialProject(
        pdf,
        {"media/clip.mp4": video},
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


def test_allowlisted_static_symlink_replacement_denied(server, tmp_path: Path):
    index = tmp_path / "static/index.html"
    index.unlink()
    index.symlink_to(tmp_path / "secret.tex")
    assert request(server, "/")[0] == 404
