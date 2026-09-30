"""Command-line interface for beamerpkg."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from .package import PackageError, extract_package, inspect_package, pack_package


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="beamerpkg",
        description="Bundle Beamer PDFs and external media into relocatable packages.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    pack = subparsers.add_parser("pack", help="create a .beamerpkg container")
    pack.add_argument("pdf", type=Path)
    pack.add_argument("--root", type=Path, default=None, help="root for media paths")
    pack.add_argument("--assets", type=Path, default=None, help="asset-list sidecar")
    pack.add_argument("--output", "-o", type=Path, default=None)
    pack.add_argument("--notes", type=Path, default=None, help="optional .pdfpc file")
    pack.add_argument(
        "--source-root",
        type=Path,
        default=None,
        help="root used to preserve editable source paths (defaults to --root)",
    )
    pack.add_argument(
        "--source",
        type=Path,
        action="append",
        default=[],
        help="editable source file or directory relative to --source-root; repeatable",
    )

    inspect = subparsers.add_parser("inspect", help="validate and describe a package")
    inspect.add_argument("package", type=Path)
    inspect.add_argument("--json", action="store_true", help="emit the manifest as JSON")

    present = subparsers.add_parser("present", help="extract and launch with pdfpc")
    present.add_argument("package", type=Path)
    present.add_argument(
        "--presenter",
        default="pdfpc",
        help="presenter executable (default: pdfpc)",
    )

    return parser


def _cmd_pack(args: argparse.Namespace) -> int:
    output = pack_package(
        args.pdf,
        root=args.root,
        asset_list=args.assets,
        output=args.output,
        notes=args.notes,
        source_root=args.source_root,
        sources=tuple(args.source),
    )
    print(output)
    return 0


def _cmd_inspect(args: argparse.Namespace) -> int:
    report = inspect_package(args.package)
    manifest = report["manifest"]
    if args.json:
        print(json.dumps(manifest, indent=2, sort_keys=True))
        return 0

    presentation = manifest["presentation"]
    assets = manifest["assets"]
    print(f"schema:       {manifest['schema_version']}")
    print(f"presentation: {presentation['path']} ({presentation['size']} bytes)")
    print(f"assets:       {len(assets)}")
    if manifest.get("notes") is not None:
        print(f"notes:        {manifest['notes']['path']}")
    source = manifest.get("source")
    if source is not None:
        print(f"source files: {len(source['files'])}")
    for asset in assets:
        print(f"  OK  {asset['path']}  {asset['size']} bytes")
    return 0


def _cmd_present(args: argparse.Namespace) -> int:
    package = args.package.resolve()
    presenter = shutil.which(args.presenter)
    if presenter is None:
        raise PackageError(f"presenter executable not found: {args.presenter}")

    with tempfile.TemporaryDirectory(prefix="beamerpkg-") as tmp:
        destination = Path(tmp)
        report = extract_package(package, destination)
        presentation = report["manifest"]["presentation"]["path"]
        completed = subprocess.run(
            [presenter, *args.presenter_args, presentation],
            cwd=destination,
            check=False,
        )
        return completed.returncode


def _split_presenter_args(argv: list[str]) -> tuple[list[str], list[str]]:
    """Split arguments after -- for transparent presenter passthrough."""

    if "--" not in argv:
        return argv, []

    separator = argv.index("--")
    cli_args = argv[:separator]
    presenter_args = argv[separator + 1 :]
    return cli_args, presenter_args


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    raw_argv = list(sys.argv[1:] if argv is None else argv)
    cli_argv, explicit_presenter_args = _split_presenter_args(raw_argv)
    args, unknown = parser.parse_known_args(cli_argv)

    if args.command == "present":
        if explicit_presenter_args and unknown:
            parser.error(
                "presenter arguments must be either after -- or passed directly, not both"
            )
        args.presenter_args = explicit_presenter_args or unknown
    else:
        if explicit_presenter_args:
            parser.error("arguments after -- are only supported by the present command")
        if unknown:
            parser.error("unrecognized arguments: " + " ".join(unknown))
        args.presenter_args = []
    try:
        if args.command == "pack":
            return _cmd_pack(args)
        if args.command == "inspect":
            return _cmd_inspect(args)
        if args.command == "present":
            return _cmd_present(args)
    except PackageError as exc:
        print(f"beamerpkg: {exc}", file=sys.stderr)
        return 2
    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
