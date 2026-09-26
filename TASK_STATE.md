# Task state

## Current objective

Validate the `PDF + relative media paths + ZIP container + pdfpc` architecture.

## Implemented

- Poetry project skeleton derived from `ukerzel/Template-` conventions.
- `beamerpkg pack`.
- `beamerpkg inspect` with size/SHA-256 verification.
- `beamerpkg present` using a temporary restored filesystem context.
- `beamerpkg.sty` with explicit `\pkgmovie` asset recording.
- Beamer/ffmpeg demo and focused tests.

## Next empirical step

Run the generated `examples/demo.beamerpkg` with pdfpc on a machine where pdfpc
video playback is available. Do not broaden implementation until that test is
performed.
