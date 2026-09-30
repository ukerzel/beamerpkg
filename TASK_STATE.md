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

## Current version

The feature branch bumps the package to 0.2.0 because PDF parsing adds a runtime
dependency (`pypdf>=5,<7`) and changes the default pack workflow.

## Next

Presenter argument passthrough is the next bounded feature. See
`docs/NEXT_STEPS.md`.
