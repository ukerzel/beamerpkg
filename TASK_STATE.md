# Task state

## Current objective

The original MVP objective — validate the `PDF + relative media paths + ZIP
container + pdfpc` architecture — is complete.

The next architecture spike remains wrapperless discovery of standard Beamer
movie annotations. A separate pdfpc-specific autoplay experiment has been added
to the demo at user request.

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

## Current demo

The demo now uses the full-size repository assets:

- `examples/media/gemini_generated_video_b2693757.mp4` (~7.85 MB);
- `examples/media/video-poster_big.png` (~2.64 MB).

The video slide uses a pdfpc-specific launch link with `autostart&loop`.
A local compile confirmed that the PDF contains the expected `/Launch`
annotation and that the asset sidecar still records the video path without query
options. Real pdfpc autoplay behavior is awaiting the next user run.

## Implemented

- Poetry project skeleton derived from `ukerzel/Template-` conventions.
- `beamerpkg pack`.
- `beamerpkg inspect` with size/SHA-256 verification.
- `beamerpkg present` using a temporary restored filesystem context.
- portable `\pkgmovie` helper for standard Beamer movie annotations.
- separate `\pkgpdfpcmovie` helper for pdfpc-specific launch-link options such
  as autoplay.
- Beamer demo with equations, TikZ, columns, overlays, full-size poster, and
  full-size MP4.
- focused tests for relocation, integrity, traversal rejection, and presenter
  working-directory behavior.
- successful real pdfpc/GStreamer click-to-play test.

## Next architecture spike

Remove the project-specific `\pkgmovie` authoring requirement by discovering
standard Beamer `\movie` media references directly from PDF annotations during
`beamerpkg pack`.

See `docs/NEXT_STEPS.md`.
