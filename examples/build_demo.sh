#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$SCRIPT_DIR"

for asset in \
  media/gemini_generated_video_b2693757.mp4 \
  media/video-poster_big.png
do
  if [[ ! -f "$asset" ]]; then
    echo "Missing committed demo asset: $asset" >&2
    exit 2
  fi
done

TEXINPUTS="../src/beamerpkg/tex//:${TEXINPUTS:-}" pdflatex -interaction=nonstopmode -halt-on-error demo.tex >/dev/null
TEXINPUTS="../src/beamerpkg/tex//:${TEXINPUTS:-}" pdflatex -interaction=nonstopmode -halt-on-error demo.tex >/dev/null

# Prove that packaging no longer depends on the LaTeX sidecar.
rm -f demo.beamerpkg-assets
poetry -C "$REPO_ROOT" run beamerpkg pack \
  "$SCRIPT_DIR/demo.pdf" \
  --root "$SCRIPT_DIR" \
  --source-root "$REPO_ROOT" \
  --source "examples/demo.tex" \
  --source "examples/media/gemini_generated_video_b2693757.mp4" \
  --source "examples/media/video-poster_big.png" \
  --source "src/beamerpkg/tex/beamerpkg.sty" \
  --output "$SCRIPT_DIR/demo.beamerpkg"

pdflatex -interaction=nonstopmode -halt-on-error wrapperless.tex >/dev/null
pdflatex -interaction=nonstopmode -halt-on-error wrapperless.tex >/dev/null
poetry -C "$REPO_ROOT" run beamerpkg pack \
  "$SCRIPT_DIR/wrapperless.pdf" \
  --root "$SCRIPT_DIR" \
  --source-root "$REPO_ROOT" \
  --source "examples/wrapperless.tex" \
  --source "examples/media/gemini_generated_video_b2693757.mp4" \
  --source "examples/media/video-poster_big.png" \
  --output "$SCRIPT_DIR/wrapperless.beamerpkg"

echo "Created examples/demo.beamerpkg and examples/wrapperless.beamerpkg"
