#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

for asset in media/video.mp4 media/video-poster.jpg; do
  if [[ ! -f "$asset" ]]; then
    echo "Missing committed demo asset: $asset" >&2
    exit 2
  fi
done

TEXINPUTS="../tex//:${TEXINPUTS:-}" pdflatex -interaction=nonstopmode -halt-on-error demo.tex >/dev/null
TEXINPUTS="../tex//:${TEXINPUTS:-}" pdflatex -interaction=nonstopmode -halt-on-error demo.tex >/dev/null
PYTHONPATH=../src python3 -m beamerpkg.cli pack demo.pdf --root .
echo "Created examples/demo.beamerpkg"
