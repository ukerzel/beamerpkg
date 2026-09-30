# Task state

## Completed

### MVP container/path validation

Validated on 2026-09-30 under WSL/WSLg with pdfpc:

- packaged PDF and relative media restoration works;
- pdfpc plays the packaged H.264 video in the TeX-defined rectangle;
- full-resolution video/poster work;
- pdfpc-specific autoplay and looping work;
- ordinary Beamer/PDF rendering remains unchanged.

### Wrapperless media discovery

Implemented and locally validated:

- standard Beamer `/Movie` annotations are discovered with `pypdf`;
- pdfpc `/Launch` media links with recognized media options are discovered;
- duplicate references are collapsed;
- remote/URI and path-traversing media references fail closed;
- unrelated launch actions are ignored;
- explicit `--assets` remains supported;
- the historical `.beamerpkg-assets` file remains a fallback;
- `examples/wrapperless.tex` uses only stock Beamer `multimedia/\movie`;
- both the mixed demo and wrapperless demo compile and package without relying
  on a sidecar.

Local evidence: 10 focused tests pass, Python compilation succeeds, and real
pdflatex output for both annotation forms packages the full 7.85 MB MP4
correctly.

### Presenter argument passthrough

Implemented for 0.2.1:

- arguments after `--` are passed to pdfpc before the extracted PDF filename;
- existing `--presenter` handling remains compatible;
- the single-monitor workflow is now `beamerpkg present talk.beamerpkg -- -w both`;
- regression coverage checks the exact subprocess argument order.

## Current version

0.2.1.

## Next

Desktop/file association and release/CI polish are the next bounded items. See
`docs/NEXT_STEPS.md`.
