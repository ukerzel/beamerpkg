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

### Optional editable source payload

Implemented for 0.3.0:

- repeatable `--source` accepts files or directories;
- `--source-root` defines the authoring tree whose relative structure is
  preserved under `source/`;
- source files are hashed and recorded separately in the manifest;
- source directories are recursive and symlinks/path escapes are rejected;
- extraction restores the editable source tree alongside runtime presentation
  files;
- the demo packages its LaTeX source, full-size assets, and
  `src/beamerpkg/tex/beamerpkg.sty`.

### Optional media

Implemented for 1.2.0 and locally verified:

- PDFs without supported media references pack with an empty `assets` list;
- empty explicit and legacy asset lists are accepted;
- PDF-only packages retain optional `.pdfpc` notes and editable source files;
- relocation and CLI presenter invocation preserve PDF, notes, and source bytes;
- missing media, unsafe paths, remote references, and unreadable PDFs still fail.

Validation: 19 tests pass; Ruff, mypy, and Poetry lock validation pass. The
relocated presenter check used a test executable; live pdfpc rendering was not
retested for this release.

## Current version

1.2.0.

Presenter passthrough accepts both an explicit `--` separator and the
separator-stripped form produced by `poetry run`.

## Next

2026-11-03 release-preparation review (current user request): fixed input-file
overwrite, archive member collisions/noncanonical manifest paths, explicit notes
naming, malformed-input exceptions, PDF false-controls decoding, and media path
normalization between routes. The user then requested additional coverage before
commit/push. This caught and fixed selection through a symlinked source parent.
Added 140 Python cases in total: 208 Python and 27 frontend tests pass. Python
statement coverage is 98.25%, branch coverage 95.39%, combined 97.40% (baseline
combined 81.85%). Ruff, mypy, Poetry lock, TypeScript/build,
wheel/sdist inventory and isolated installed-wheel route proof pass. Detailed
findings and evidence paths are in `WORKLOG.md`. User authorized commit/push of
these reviewed fixes. Version remains 1.2.0 and builds are local validation
artifacts. Version selection, release metadata, tagging and publication remain
for the release step. No new live pdfpc or Python-version/browser-matrix
qualification is claimed.

2026-11-03: the spatial route was merged into `main` at the user's instruction,
after the user's walkthrough. The pre-merge audit fixes are in `b995141`. Final
check: 68 Python and 27 frontend tests, Ruff, mypy, TypeScript and the
installed-wheel proof. Remaining deferred work is in `issues.md` (Deferred).
The history below is kept as it was.

The user-authorized first spatial MVP S0–S4 is technically complete on
`feat/spatial-prototype`; stop after final S4 commit/push. Human walkthrough
and the proceed/revise/stop product decision remain pending. No further editor,
save API, release, or merge is authorized. Active Batch: `issues.md`.

Commits: plan/cold read `2fa9f70`, admission/model/media `20bd4de`, browser
feasibility/DOM decision `1b41ff0`, read-only viewer `5450649`, runtime-asset
boundary `af80080`. All were pushed to the configured same-name upstream.
The branch starts at `2e86c6f3be328f6c55d42ac0d792084d1372e95d`;
`main` and `package.py` remain unchanged.

Final validation: 59 Python tests and 21 frontend tests pass, plus Ruff, mypy
(seven source files), Poetry lock, TypeScript/build and installed-wheel proof.
The installed runtime has no Node/npm/pdfpc on PATH; media plays/seeks through
206 responses, history restores paused, non-local browser requests are blocked,
and process-private temporary files are removed. No new live pdfpc or human
lecture claim is made. Evidence/source hashes:
`docs/spatial/evidence/s4-20261101/distribution.json`.

Try: `poetry run beamerpkg spatial build/spatial-fixtures/science.beamerpkg`.
Read `docs/spatial/USER_GUIDE.md` and `PROTOTYPE_EVALUATION.md` for limitations.
Compiled app assets are ignored/rebuildable; preserve them under ignored build/
before a later main-only build, since generated files are not branch-isolated.
Experimental wheel/sdist are in `build/spatial-dist`; the published 1.2.0 files
in dist/ were restored from PyPI and hash-verified after an initial output-path
mistake. The prototype still has local package version 1.2.0, not a new release.

Preserve unrelated untracked `examples/wrapperless.pdf`. Existing-route
desktop/release polish remains deferred in `docs/NEXT_STEPS.md`.
