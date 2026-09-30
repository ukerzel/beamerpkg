# Task state

## Current objective

The original MVP objective — validate the `PDF + relative media paths + ZIP
container + pdfpc` architecture — is complete.

## MVP result

**Validated on 2026-09-30 under WSL/WSLg with pdfpc.**

Observed end-to-end behavior:

- `beamerpkg present examples/demo.beamerpkg` restored the packaged PDF and
  relative media path correctly.
- pdfpc detected the Beamer movie annotation and opened the packaged MP4.
- after installing the required local GStreamer H.264 decoder, clicking the
  poster played the video in the TeX-defined rectangle;
- ordinary Beamer rendering and overlays remained PDF/Beamer behavior.
- running `pdfpc examples/demo.pdf` directly produced the same click-to-play
  behavior, confirming that the package layer adds no rendering-specific
  behavior.

The static poster before a click is normal pdfpc behavior for this annotation
path, not a beamerpkg failure.

## Implemented

- Poetry project skeleton derived from `ukerzel/Template-` conventions.
- `beamerpkg pack`.
- `beamerpkg inspect` with size/SHA-256 verification.
- `beamerpkg present` using a temporary restored filesystem context.
- `beamerpkg.sty` with explicit `\pkgmovie` asset recording.
- Beamer demo with equations, TikZ, columns, overlays, poster image, and MP4.
- focused tests for relocation, integrity, traversal rejection, and presenter
  working-directory behavior.
- successful real pdfpc/GStreamer playback test.

## Next spike

Remove the project-specific `\pkgmovie` authoring requirement by discovering
standard Beamer `\movie` media references directly from PDF annotations during
`beamerpkg pack`.

Do not start autoplay, GUI/file-association work, or a new renderer in the same
change. See `docs/NEXT_STEPS.md`.
