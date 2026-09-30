#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

for asset in \
  media/gemini_generated_video_b2693757.mp4 \
  media/video-poster_big.png
do
  if [[ ! -f "$asset" ]]; then
    echo "Missing committed demo asset: $asset" >&2
    exit 2
  fi
done

TEXINPUTS="../tex//:${TEXINPUTS:-}" pdflatex -interaction=nonstopmode -halt-on-error demo.tex >/dev/null
TEXINPUTS="../tex//:${TEXINPUTS:-}" pdflatex -interaction=nonstopmode -halt-on-error demo.tex >/dev/null

# Prove that packaging no longer depends on the LaTeX sidecar.
rm -f demo.beamerpkg-assets
PYTHONPATH=../src python3 -m beamerpkg.cli pack demo.pdf --root .

pdflatex -interaction=nonstopmode -halt-on-error wrapperless.tex >/dev/null
pdflatex -interaction=nonstopmode -halt-on-error wrapperless.tex >/dev/null
PYTHONPATH=../src python3 -m beamerpkg.cli pack wrapperless.pdf --root .

echo "Created examples/demo.beamerpkg and examples/wrapperless.beamerpkg"
