"""Read-only, allowlisted loopback serving for the spatial presentation route."""

from __future__ import annotations

import json
import mimetypes
import re
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from pathlib import Path
from typing import cast
from urllib.parse import unquote, urlsplit

from .package import PackageError
from .spatial_project import SpatialProject, load_project

CSP = (
    "default-src 'none'; script-src 'self' 'wasm-unsafe-eval'; "
    "worker-src 'self' blob:; style-src 'self' 'unsafe-inline'; "
    "font-src 'self' blob: data:; img-src 'self' blob: data:; "
    "media-src 'self'; connect-src 'self'; object-src 'none'; "
    "base-uri 'none'; frame-ancestors 'none'"
)


def _range(raw: str, length: int) -> tuple[int, int]:
    match = re.fullmatch(r"bytes=(\d*)-(\d*)", raw)
    if not match or length == 0:
        raise ValueError("unsupported range")
    start, end = match.groups()
    if not start:
        suffix = int(end or "0")
        if suffix <= 0:
            raise ValueError("invalid suffix")
        return max(0, length - suffix), length - 1
    first = int(start)
    last = min(int(end), length - 1) if end else length - 1
    if first >= length or last < first:
        raise ValueError("unsatisfiable range")
    return first, last


def make_server(
    project: SpatialProject, static: Path | None = None
) -> ThreadingHTTPServer:
    """Create an ephemeral loopback server; caller owns serving and cleanup."""
    static = (static or Path(str(files("beamerpkg") / "static/spatial"))).resolve()
    if not (static / "index.html").is_file():
        raise PackageError(
            "spatial frontend missing; run npm ci && npm run build in frontend/spatial"
        )
    allowlist: dict[str, tuple[Path, Path]] = {}
    for path in static.rglob("*"):
        if path.is_file() and not path.is_symlink():
            allowlist["/" + path.relative_to(static).as_posix()] = (path, static)
    allowlist["/"] = (static / "index.html", static)
    allowlist["/runtime/document.pdf"] = (project.pdf, project.pdf.parent)
    urls: dict[str, str] = {}
    referenced = {p["asset_path"] for p in project.data["placements"]}
    runtime_media = (
        (asset, path) for asset, path in project.assets.items() if asset in referenced
    )
    for index, (asset, path) in enumerate(runtime_media):
        url = f"/runtime/asset-{index}"
        allowlist[url] = (path, path.parent)
        urls[asset] = url
    data = {
        **project.data,
        "pdf_url": "/runtime/document.pdf",
        "placements": [
            {**p, "url": urls[p["asset_path"]]} for p in project.data["placements"]
        ],
    }
    payload = json.dumps(data, allow_nan=False).encode()

    class Handler(BaseHTTPRequestHandler):
        def setup(self) -> None:
            super().setup()
            self.connection.settimeout(10)

        def log_message(self, format: str, *args: object) -> None:
            """No request or filesystem-path logging."""

        def _headers(
            self,
            status: int,
            length: int,
            content_type: str = "text/plain",
            extra: dict[str, str] | None = None,
        ) -> None:
            self.send_response(status)
            self.send_header("Content-Length", str(length))
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Security-Policy", CSP)
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Cache-Control", "no-store")
            for key, value in (extra or {}).items():
                self.send_header(key, value)
            self.end_headers()

        def _serve(self, head: bool = False) -> None:
            endpoint = f"127.0.0.1:{cast(ThreadingHTTPServer, self.server).server_port}"
            hosts = self.headers.get_all("Host") or []
            origins = self.headers.get_all("Origin") or []
            if hosts != [endpoint] or (origins and origins != [f"http://{endpoint}"]):
                self._headers(403, 0)
                return
            try:
                parsed = urlsplit(self.path)
                path = unquote(parsed.path, errors="strict")
                if parsed.scheme or parsed.netloc:
                    raise ValueError("absolute target")
            except (ValueError, UnicodeError):
                self._headers(404, 0)
                return
            if path == "/api/project":
                self._headers(200, len(payload), "application/json")
                if not head:
                    self.wfile.write(payload)
                return
            entry = allowlist.get(path)
            if entry is None:
                self._headers(404, 0)
                return
            file, boundary = entry
            try:
                if file.is_symlink() or not file.resolve().is_relative_to(boundary):
                    self._headers(404, 0)
                    return
                with file.open("rb") as handle:
                    length = file.stat().st_size
                    first, last, status = 0, length - 1, 200
                    extra = {"Accept-Ranges": "bytes"}
                    ranges = self.headers.get_all("Range") or []
                    if ranges:
                        try:
                            if len(ranges) != 1 or len(ranges[0]) > 128:
                                raise ValueError("multiple or oversized ranges")
                            first, last = _range(ranges[0], length)
                        except ValueError:
                            self._headers(
                                416, 0, extra={"Content-Range": f"bytes */{length}"}
                            )
                            return
                        status = 206
                        extra["Content-Range"] = f"bytes {first}-{last}/{length}"
                    remaining = max(0, last - first + 1)
                    content_type = (
                        mimetypes.guess_type(str(file))[0] or "application/octet-stream"
                    )
                    if path.startswith(
                        "/runtime/asset-"
                    ) and not content_type.startswith(("video/", "audio/")):
                        content_type = "application/octet-stream"
                        extra["Content-Disposition"] = "attachment"
                    self._headers(status, remaining, content_type, extra)
                    if head:
                        return
                    handle.seek(first)
                    while remaining:
                        chunk = handle.read(min(64 * 1024, remaining))
                        if not chunk:
                            break
                        self.wfile.write(chunk)
                        remaining -= len(chunk)
            except FileNotFoundError:
                self._headers(404, 0)
            except (OSError, ValueError):
                self.close_connection = True

        def do_GET(self) -> None:
            self._serve()

        def do_HEAD(self) -> None:
            self._serve(head=True)

        def do_PUT(self) -> None:
            self.close_connection = True
            self._headers(405, 0, extra={"Allow": "GET, HEAD"})

        do_POST = do_PUT
        do_DELETE = do_PUT
        do_PATCH = do_PUT
        do_OPTIONS = do_PUT

    return ThreadingHTTPServer(("127.0.0.1", 0), Handler)


def run_spatial(package: Path, *, open_browser: bool = True) -> int:
    """Keep verified temporary files alive until the foreground server stops."""
    with load_project(package.resolve()) as project:
        server = make_server(project)
        try:
            url = f"http://127.0.0.1:{server.server_port}/"
            print(f"Spatial viewer: {url}\nCtrl+C to stop.", flush=True)
            if open_browser and not webbrowser.open(url):
                print(
                    "No browser opened; open the displayed local URL manually.",
                    file=sys.stderr,
                )
            server.serve_forever(poll_interval=0.2)
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
    return 0
