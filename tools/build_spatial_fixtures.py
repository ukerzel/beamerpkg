"""Build isolated real fixtures without overwriting the user's example outputs."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from dataclasses import asdict
from pathlib import Path

from pypdf import PdfReader, PdfWriter

from beamerpkg.package import pack_package
from beamerpkg.spatial_project import load_project


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    build = root / "build/spatial-fixtures"
    build.mkdir(parents=True, exist_ok=True)
    authoring = build / "authoring"
    authoring.mkdir(exist_ok=True)
    shutil.copytree(root / "examples/media", authoring / "media", dirs_exist_ok=True)
    env = os.environ.copy()
    env["TEXINPUTS"] = (
        str(root / "src/beamerpkg/tex") + "//:" + env.get("TEXINPUTS", "")
    )
    for name in ("demo", "wrapperless", "science"):
        source = root / (
            f"examples/spatial/{name}.tex"
            if name == "science"
            else f"examples/{name}.tex"
        )
        shutil.copyfile(source, authoring / f"{name}.tex")
        with (build / f"{name}-build.txt").open("w") as log:
            for _ in range(2):
                subprocess.run(
                    [
                        "pdflatex",
                        "-interaction=nonstopmode",
                        "-halt-on-error",
                        f"{name}.tex",
                    ],
                    cwd=authoring,
                    env=env,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    check=True,
                )
        pack_package(
            authoring / f"{name}.pdf",
            root=authoring,
            output=build / f"{name}.beamerpkg",
        )
    writer = PdfWriter()
    reader = PdfReader(authoring / "demo.pdf")
    for index in range(40):
        writer.add_page(reader.pages[index % len(reader.pages)])
    writer.write(authoring / "stress.pdf")
    pack_package(
        authoring / "stress.pdf", root=authoring, output=build / "stress.beamerpkg"
    )
    public = root / "frontend/spatial/public/_probe"
    public.mkdir(parents=True, exist_ok=True)
    inventory = {}
    for name in ("demo", "wrapperless", "science", "stress"):
        with load_project(build / f"{name}.beamerpkg") as project:
            shutil.copyfile(project.pdf, public / f"{name}.pdf")
            data = project.data
            data["pdf_url"] = f"/_probe/{name}.pdf"
            for index, (asset, path) in enumerate(project.assets.items()):
                media_name = f"asset-{index}.mp4"
                shutil.copyfile(path, public / media_name)
                for placement in data["placements"]:
                    if placement["asset_path"] == asset:
                        placement["url"] = f"/_probe/{media_name}"
            (public / f"{name}.json").write_text(json.dumps(data))
            inventory[name] = {
                "pdf_sha256": hashlib.sha256(project.pdf.read_bytes()).hexdigest(),
                "pages": len(data["pages"]),
                "placements": data["placements"],
            }
            if name == "science":
                layout = data["layout"]
                layout["frames"][1]["page_indices"] = [1, 2, 3]
                layout["frames"] = [
                    f for f in layout["frames"] if f["id"] not in {"f2", "f3"}
                ]
                layout["objects"] = [
                    o for o in layout["objects"] if o["id"] not in {"o2", "o3"}
                ]
                layout["viewpoints"] = [
                    v for v in layout["viewpoints"] if v["id"] not in {"v2", "v3"}
                ]
                layout["viewpoints"].append(
                    {
                        "id": "detail",
                        "target": {
                            "kind": "object",
                            "object_id": "o1",
                            "region": [0, 0.2, 0.52, 0.65],
                        },
                    }
                )
                layout["paths"][0]["steps"] = [
                    s
                    for s in layout["paths"][0]["steps"]
                    if s["id"] not in {"s2", "s3"}
                ]
                layout["paths"][0]["steps"].insert(
                    2,
                    {
                        "id": "detail-step",
                        "viewpoint_id": "detail",
                        "overlay_policy": "fixed",
                        "overlay_index": 2,
                    },
                )
                (build / "science.spatial.json").write_text(
                    json.dumps(layout, indent=2)
                )
    geometry = PdfWriter()
    geometry.add_page(PdfReader(authoring / "science.pdf").pages[1])
    page = geometry.pages[0]
    page.cropbox.lower_left = (20, 15)
    page.cropbox.upper_right = (420, 240)
    page.rotate(90)
    geometry.write(public / "rotated.pdf")
    (build / "inventory.json").write_text(json.dumps(inventory, indent=2))
    print(
        json.dumps(
            {
                name: {"pages": value["pages"], "pdf_sha256": value["pdf_sha256"]}
                for name, value in inventory.items()
            },
            indent=2,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
