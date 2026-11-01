"""Prove a built spatial wheel from an isolated, relocated offline runtime."""

from __future__ import annotations

import hashlib
import json
import os
import re
import selectors
import shutil
import signal
import subprocess
import tarfile
import tempfile
import time
import tomllib
import venv
import zipfile
from importlib.metadata import version
from pathlib import Path
from urllib.request import Request, urlopen


def run(command: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> str:
    result = subprocess.run(
        command, cwd=cwd, env=env, capture_output=True, text=True, timeout=120
    )
    if result.returncode:
        raise RuntimeError(
            f"command failed: {command[0]}\n{result.stdout}\n{result.stderr}"
        )
    return result.stdout.strip()


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    report = root / "build/spatial-evidence/s4"
    report.mkdir(parents=True, exist_ok=True)
    package_version = tomllib.loads((root / "pyproject.toml").read_text())["project"][
        "version"
    ]
    wheel = (
        root / "build/spatial-dist" / f"beamerpkg-{package_version}-py3-none-any.whl"
    )
    sdist = root / "build/spatial-dist" / f"beamerpkg-{package_version}.tar.gz"
    with zipfile.ZipFile(wheel) as archive:
        wheel_names = archive.namelist()
    with tarfile.open(sdist) as archive:
        sdist_names = archive.getnames()
    for names in (wheel_names, sdist_names):
        for fragment in (
            "static/spatial/index.html",
            "static/spatial/assets/pdf.worker",
            "static/spatial/pdfjs/cmaps/",
            "static/spatial/pdfjs/standard_fonts/",
            "static/spatial/pdfjs/iccs/",
            "static/spatial/pdfjs/wasm/",
            "static/spatial/THIRD_PARTY_NOTICES.txt",
            "tex/beamerpkg.sty",
        ):
            assert any(fragment in name for name in names), fragment
        assert not any(
            "node_modules" in name or "probe.html" in name or "_probe/" in name
            for name in names
        )
    dependencies = list(
        (Path.home() / ".cache/pypoetry/artifacts").rglob(
            f"pypdf-{version('pypdf')}-*.whl"
        )
    )
    if not dependencies:
        raise RuntimeError(
            "Retain the installed pypdf wheel in Poetry's cache before this offline check"
        )
    print("Distribution asset inventory passed; creating isolated runtime.", flush=True)
    with tempfile.TemporaryDirectory(prefix="beamerpkg-installed-proof-") as tmp:
        work = Path(tmp)
        temp_root = work / "temporary"
        temp_root.mkdir()
        environment = work / "venv"
        venv.EnvBuilder(with_pip=True).create(environment)
        python = environment / "bin/python"
        runtime_env = {
            key: value
            for key, value in os.environ.items()
            if not key.startswith("PIP_")
            and key not in {"PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV"}
        }
        runtime_env.update(
            PATH=str(environment / "bin"),
            TMPDIR=str(temp_root),
            PIP_NO_INDEX="1",
            PIP_CONFIG_FILE="/dev/null",
            PIP_DISABLE_PIP_VERSION_CHECK="1",
        )
        run(
            [
                str(python),
                "-m",
                "pip",
                "install",
                "--no-index",
                "--no-deps",
                "--no-cache-dir",
                str(wheel),
                str(dependencies[0]),
            ],
            cwd=work,
            env=runtime_env,
        )
        origin = json.loads(
            run(
                [
                    str(python),
                    "-c",
                    "import json,shutil,hashlib,beamerpkg.spatial_server as s; from pathlib import Path; p=Path(s.__file__); print(json.dumps({'module':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'node':shutil.which('node'),'npm':shutil.which('npm'),'pdfpc':shutil.which('pdfpc')}))",
                ],
                cwd=work,
                env=runtime_env,
            )
        )
        assert not Path(origin["module"]).is_relative_to(root)
        assert origin["sha256"] == digest(root / "src/beamerpkg/spatial_server.py")
        assert origin["node"] is origin["npm"] is origin["pdfpc"] is None
        package = work / "science.beamerpkg"
        shutil.copyfile(root / "build/spatial-fixtures/science.beamerpkg", package)
        sidecar = package.with_suffix(".spatial.json")
        shutil.copyfile(root / "build/spatial-fixtures/science.spatial.json", sidecar)
        original_hash = digest(package)
        executable = environment / "bin/beamerpkg"
        # The old route must ignore a stale sidecar even in the installed wheel.
        saved = sidecar.read_bytes()
        sidecar.write_text("not valid JSON")
        inspected = json.loads(
            run(
                [str(executable), "inspect", str(package), "--json"],
                cwd=work,
                env=runtime_env,
            )
        )
        rejected = subprocess.run(
            [str(executable), "spatial", str(package), "--no-browser"],
            cwd=work,
            env=runtime_env,
            capture_output=True,
            text=True,
            timeout=20,
        )
        assert rejected.returncode == 2 and "spatial layout" in rejected.stderr
        sidecar.write_bytes(saved)
        presenter = work / "fake-presenter"
        receipt = work / "presenter.json"
        presenter.write_text(
            f"#!{python}\nimport sys,json\nfrom pathlib import Path\nPath({str(receipt)!r}).write_text(json.dumps({{'arguments':sys.argv[1:],'pdf_exists':Path(sys.argv[-1]).is_file()}}))\n"
        )
        presenter.chmod(0o700)
        run(
            [
                str(executable),
                "present",
                str(package),
                "--presenter",
                str(presenter),
                "--",
                "-w",
                "both",
            ],
            cwd=work,
            env=runtime_env,
        )
        native = json.loads(receipt.read_text())
        assert native == {
            "arguments": ["-w", "both", "science.pdf"],
            "pdf_exists": True,
        }
        previous = set(temp_root.glob("beamerpkg-spatial-*")) | set(
            temp_root.glob("beamerpkg-admission-*")
        )
        server = subprocess.Popen(
            [str(executable), "spatial", str(package), "--no-browser"],
            cwd=work,
            env=runtime_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            selector = selectors.DefaultSelector()
            selector.register(server.stdout, selectors.EVENT_READ)
            endpoint = ""
            deadline = time.monotonic() + 20
            while time.monotonic() < deadline:
                if selector.select(timeout=1):
                    line = server.stdout.readline()  # type: ignore[union-attr]
                    match = re.search(r"http://127\.0\.0\.1:\d+/", line)
                    if match:
                        endpoint = match[0]
                        break
                if server.poll() is not None:
                    raise RuntimeError("installed server exited before readiness")
            selector.close()
            assert endpoint, "installed server did not start"
            with urlopen(endpoint + "api/project", timeout=10) as response:
                project = json.load(response)
            assert (
                project["source"]["pdf_sha256"] == inspected["presentation"]["sha256"]
            )
            asset = project["placements"][0]["url"]
            with urlopen(
                Request(endpoint.rstrip("/") + asset, headers={"Range": "bytes=0-31"}),
                timeout=10,
            ) as response:
                assert response.status == 206 and len(response.read()) == 32
                range_header = response.headers["Content-Range"]
            print(
                "Installed route isolation passed; running local-only browser walkthrough.",
                flush=True,
            )
            browser = json.loads(
                run(
                    [
                        "node",
                        "scripts/installed-proof.mjs",
                        endpoint,
                        str(report / "installed.png"),
                    ],
                    cwd=root / "frontend/spatial",
                    env=os.environ.copy(),
                )
            )
        finally:
            server.send_signal(signal.SIGINT)
            server.communicate(timeout=15)
        assert server.returncode == 0
        remaining = set(temp_root.glob("beamerpkg-spatial-*")) | set(
            temp_root.glob("beamerpkg-admission-*")
        )
        assert not remaining - previous, (
            "installed server left extraction/admission directories"
        )
        assert digest(package) == original_hash
        result = {
            "source_base_commit": run(["git", "rev-parse", "HEAD"], cwd=root),
            "working_tree_source_sha256": {
                path.relative_to(root).as_posix(): digest(path)
                for folder in (root / "src/beamerpkg", root / "frontend/spatial/src")
                for path in sorted(folder.iterdir())
                if path.suffix in {".py", ".ts", ".tsx", ".css"}
            },
            "wheel": {
                "name": wheel.name,
                "sha256": digest(wheel),
                "size": wheel.stat().st_size,
                "members": len(wheel_names),
            },
            "sdist": {
                "name": sdist.name,
                "sha256": digest(sdist),
                "size": sdist.stat().st_size,
                "members": len(sdist_names),
            },
            "installed_module_outside_checkout": True,
            "installed_module_sha256": origin["sha256"],
            "runtime_path_has_node_npm_pdfpc": False,
            "installation": "no-index, no-deps, local wheel + cached pypdf wheel",
            "pypdf": version("pypdf"),
            "archive_unchanged": True,
            "invalid_sidecar_ignored_by_inspect": True,
            "invalid_sidecar_rejected_by_spatial": True,
            "presenter_test": native,
            "presenter_evidence_scope": "fake subprocess; no live pdfpc rendering claim",
            "media_range": range_header,
            "temporary_files_removed": True,
            "browser": browser,
        }
        (report / "distribution.json").write_text(json.dumps(result, indent=2))
        print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
