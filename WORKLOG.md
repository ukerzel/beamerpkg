# Work log

## 2026-11-01 — first spatial MVP plan and cold read (S0)

- User created `feat/spatial-prototype` from package 1.2.0, then authorized
  planning, cold read, commit/push, and execution through the first-MVP ladder.
- Narrowed the first slice to a read-only spatial presenter using optional
  hand-authored JSON. Full editor/write API remains in the broader plan.
- Applied scientific-plan-hardener to coordinate/evidence/ownership boundaries;
  no scientific physical model is changed. Self-review findings and amendments
  are recorded in `docs/spatial/COLD_READ.md`.
- Existing untracked `examples/wrapperless.pdf` is unrelated generated material
  and is excluded from scoped commits.
- Branch initially has no upstream; publication awaits user-side same-name
  upstream setup supported by the installed Git guard.
- S0 validation: 19 pytest tests passed; Ruff passed; mypy passed for all four
  existing source files; plan code fences and illustrative JSON checked.

## 2026-11-01 — S1 admission, sidecar model, media inventory

- S0 committed/pushed as `2fa9f70`; user configured the same-name upstream.
- New spatial-only admission pins a private archive copy, bounds metadata and
  actual expanded reads, and rejects duplicate/noncanonical paths and symlinks.
- Strict sidecar parser rejects duplicate keys/nonfinite numbers; validates
  binding, IDs/references, consecutive nonoverlapping geometry-compatible groups,
  regions, policies and limits. Default import makes no overlay guesses.
- Added placement API alongside unchanged deduplicated discovery; validates
  manifest membership, rectangles, and supported movie/query flags.
- TDD began with missing-module/API failures; 22 focused and 41 total pytest
  tests now pass. Ruff passes; mypy passes for six source files.
- Existing demo archive yields both real placements with distinct page/annotation
  identity and encoded repeat/controls/autostart flags. Browser behavior and
  rebuilt-fixture evidence remain S2 work, not established by these tests.

## 2026-11-01 — S2 browser feasibility

- S1 committed/pushed as `20bd4de`. Pinned frontend tools and Chromium installed
  with writable /tmp caches; normal npm cache was read-only, then corrected.
- Fresh isolated TeX builds preserve user's example outputs. Science fixture
  has eight pages and explicit three-overlay grouping; stress repeats real
  pages to 40 and is labelled repeated-content stress.
- Both adapters passed real video continuity, local-only resource loading and
  independently specified cropped/rotated geometry on two browser runs.
- Inspected PDF.js science screenshot against Poppler; readable formulas,
  translucent bands and layout retained. Fine antialiasing differences noted.
- Selected DOM by ADR-001 for the graph-free presentation consumer. Measured
  timings/heap/TaskDuration are diagnostics, not a speed or memory-superiority
  claim. Small immutable evidence retained in `docs/spatial/evidence/s2-20261101`.
- Installed PDF.js 6 uses loadingTask teardown; initial TypeScript errors exposed
  that API mismatch and missing Node type declarations, then were corrected.
- S3 must still establish full navigation, bounded rendering/media policy,
  safe serving and route independence. No product acceptance is asserted.
- An added overlay-swap probe hit Playwright's implicit five-second readiness
  assertion for DOM. Retained trace/error context before retry; readiness now
  has a bounded 45-second wait because startup is diagnostic, not a speed gate.
  Both adapters then passed, including same-surface overlay swaps. Earlier
  successful measurements remain immutable and are not a startup guarantee.

## 2026-11-01 — S3 usable read-only viewer

- S2 committed/pushed as `1b41ff0`. Added lazy opt-in CLI, bounded read-only
  loopback server, runtime browser model validation, guided/history controller,
  cancelable semantic camera, clipped rendering queue, and independent media.
- Per-talk route isolation has fresh-process tests; static HTTP has no source
  tree exposure or write API. HEAD/range and host/origin controls pass.
- A real sidebar-resize/focus interruption failed the stronger video-detail
  test; retained the trace and corrected pending-target handling. An earlier
  stale-bundle test run after a failed typecheck is recorded separately.
- Added native media-event status updates and paused-frame restoration. One
  extra developer dependency, pinned Prettier, formats frontend code for review;
  it is not shipped as runtime JavaScript. Runtime Python dependencies unchanged.
- 57 Python tests and 18 frontend tests passed; Ruff/mypy (seven source files),
  Poetry lock check, frontend typecheck/build passed. Retained sharp screenshot
  and buffer dimensions; installed-distribution and human checks remain S4.

## 2026-11-01 — S4 runtime-asset boundary correction

- S3 published as `5450649`. First installed-wheel proof passed with Node/npm/
  pdfpc absent from runtime PATH, no non-local browser requests, real MP4 seek
  and 206 responses, paused restore and cleanup. Final proof will be repeated
  after the boundary correction below.
- Review found the HTTP allowlist included every declared runtime asset, even
  those not referenced by a media placement. A new HTTP regression failed
  (unreferenced HTML returned 200). Serve referenced placement assets only and
  force non-media payloads to attachment/octet-stream with nosniff, so archive
  files cannot become same-origin executable HTML/JS through that route.
- Experimental builds now use `build/spatial-dist`. The first build reused
  `dist/` release filenames and an initial helper glob selected an old 1.0.1
  wheel. Restored the published 1.2.0 wheel/sdist from PyPI and verified official
  hashes; retained restoration receipt. No artifact was published or released.
- Boundary correction validation: regression first returned 200 instead of
  expected 404; now 59 Python tests pass, including non-executable handling of
  a referenced HTML payload. Ruff and mypy (seven source files) pass.

## 2026-11-01 — S4 installed-distribution proof and named stop

- Runtime-asset follow-up published as `af80080`. Final experimental wheel and
  sdist built to `build/spatial-dist`; both contain local app/worker/resources,
  notices and the existing TeX helper. No probe/Node modules are shipped.
- Final installed proof passes from a fresh no-index environment outside the
  checkout, with Node/npm/pdfpc absent on runtime PATH. Real relocated MP4
  plays/seeks through 206 responses, same-instance detail retains the element,
  overview/history restores paused, original archive bytes remain unchanged,
  and the foreground server removes its private temporary files on SIGINT.
- External browser requests are blocked; zero external attempts/page errors.
  This is browser-request isolation, not OS-level networking isolation. The
  fake native presenter proves extraction/argument order only.
- A concurrent-test false cleanup failure used shared /tmp; retained its
  diagnosis/screenshot and changed the proof to a process-private TMPDIR.
- Final frontend suite: 21 passed, including HiDPI DPR 2, deep clipped zoom,
  reduced motion, interrupted focus/sidebar resize, and malformed decode bytes.
  Python: 59 passed; Ruff/mypy, Poetry lock, strict TS/build passed. Media
  overlays clip at the page boundary; rotated-video orientation is not qualified.
- Final receipt binds exact wheel/sdist/source hashes. Immutable evidence:
  `docs/spatial/evidence/s4-20261101`. Release artifacts restored and verified;
  no main change, release, merge, or unrelated-PDF mutation.
- Applied research-surface-triage: keep the selected prototype route, comparison
  and fixture tools, and evidence in their stated roles. No cleanup/movement or
  automatic feature promotion follows from that classification.
- Added try-it/stop instructions and an evidence-limited evaluation. Technical
  S0–S4 is complete; commit/push final S4 slice, then stop for human walkthrough
  and the next product decision. Full editor/save and lecturer parity remain
  deferred rather than silently claimed.

## 2026-11-03 — Code review and release preparation

User requested a code/bug/test review with coverage before another release.
Reviewed the Python package/CLI, spatial admission/model/server and browser
model/navigation/rendering/media code. No release, tag, push or version change.

Findings fixed, ordered by impact:

- **High: packing could overwrite an input file.** `--output talk.pdf`, a media
  filename, the notes file or asset-list file replaced that input with a ZIP.
  Reject output/input identity before writing; regressions assert original bytes.
- **Medium: packing could produce an archive its own validator rejected.**
  Notes/media/source names could collide, including file/directory prefixes.
  Validate all member paths together before replacing the destination. Failed
  writes also retain the previous bundle and remove temporary output.
- **Medium: manifest paths and ZIP entries were validated inconsistently.**
  Noncanonical paths could pass hash validation and later trigger `KeyError` or
  extraction errors. Duplicate file records and file/directory conflicts could
  pass inspection; ZIP symlinks passed inspection but failed extraction. Require
  canonical unique paths without file/directory conflicts, and reject symlinks
  during inspection. Boolean schemas and noninteger sizes are rejected.
- **Medium: explicit notes with a different filename were invisible to pdfpc.**
  Store selected notes under the PDF stem plus `.pdfpc`. A relocated package
  regression checks notes/source bytes through presenter invocation and spatial
  loading. Documented this behavior in README.
- **Medium: media paths accepted by packing could fail spatial loading.**
  Normalize harmless `./` and repeated separators consistently, retaining the
  unchanged PDF and canonical packaged asset. Both routes are covered.
- **Medium: PDF `/ShowControls false` became `true`.** pypdf's `BooleanObject`
  is truthy even when its `.value` is false. Decode that value explicitly; test
  both true and false.
- **Medium: malformed inputs could escape as tracebacks.** Empty normalized
  paths such as `.`, NUL-containing names, malformed annotation arrays, oversized
  sidecar integers, deeply nested manifest JSON, encrypted ZIP entries and
  unsupported compression now fail as controlled package/media errors.

Added 54 Python test cases, including the regressions above, tampered hashes,
invalid manifests, undeclared/missing members, destination symlink escapes,
atomic-write failure, file-spec dictionaries and CLI reports/errors. Retained
failing-before evidence in `build/release-review/regressions-before.log` and
`media-regressions-before.log`.

Validation:

- 122 Python tests and 27 Playwright tests pass on Python 3.14.4/Chromium.
- Statement coverage: 85.68% -> 90.82%; branch coverage: 72.70% -> 80.49%;
  combined coverage: 81.85% -> 87.74%. Coverage measures Python only.
- Ruff, mypy (seven source files), Poetry lock validation, TypeScript and
  frontend production build pass.
- Rebuilt real demo/wrapperless/science/stress fixtures. Local wheel and sdist
  include offline frontend resources, notices and the TeX helper.
- Fresh offline installation outside the checkout passes route isolation,
  relocated presenter invocation, browser playback/seeking through HTTP 206,
  paused restore, unchanged archive and private temporary-file cleanup. The
  installed runtime PATH has no Node/npm/pdfpc; the browser driver runs outside
  that runtime. No external browser requests or page errors occurred.
- Receipts, logs, HTML/XML/JSON coverage and distribution hashes are under
  `build/release-review/`; the installed proof also writes
  `build/spatial-evidence/s4/distribution.json`.

The first installed proof omitted `PLAYWRIGHT_BROWSERS_PATH` and could not find
Chromium. Its failure log is retained; rerunning with the documented browser
path passed. An overlapping frontend invocation hit the existing development
port; subsequent isolated frontend runs passed. These are environment/setup
failures, not product regressions.

Release boundaries: version remains 1.2.0; builds in `build/spatial-dist` are
validation artifacts, not a new release. Version/metadata selection and final
release build/tag/publication remain. Live pdfpc rendering, Python 3.11–3.13
and other browsers were not requalified. Python coverage still leaves parser,
resource-limit and environment-error branches unexercised; frontend statement
coverage was not collected. User authorized committing/pushing the reviewed
fixes. Preserved the unrelated untracked `examples/wrapperless.pdf` and existing
immutable spatial receipts.

### Follow-up: targeted coverage before commit/push

The user requested further coverage rather than deferring it. Added 86 more
Python cases for source symlinks at each depth, source-root escapes, invalid
pack inputs and manifest collections, unsupported movie/launch options,
unknown playback flags, layout references/limits/world views, growing archives,
invalid sidecars and cleanup, page counts/rotation/UserUnit, HTTP methods,
ranges and invalid targets, presenter failure cleanup and browser fallback.

This caught an additional bug: `--source linked/plot.png` accepted a symlinked
parent even though selecting the link directly was rejected. Resolution could
silently change the archived source path. Source selection now checks every
input component for symlinks before collecting files. Retained the failing
regression in `build/release-review/coverage-extension-package-before.log`.

Final Python validation is **208 passed**. Statement coverage is **98.25%**,
branch coverage **95.39%**, combined **97.40%**. These supersede the initial
review's 122-test/87.74% totals above; the initial coverage and test receipt are
retained separately. The spatial model has 100% measured statement/branch
coverage. Remaining gaps are defensive checks and unusual parser/IO/resource
failure paths; no artificial exclusions or coverage thresholds were added.

Ruff, mypy, Poetry lock and diff checks pass. Frontend source/assets are
unchanged from the passing 27-test/TypeScript/build check. Rebuilt wheel/sdist
and refreshed the isolated installed-wheel proof for the final Python source.
Publication/version boundaries and live-pdfpc/browser-matrix limitations above
still apply. The user authorized committing and pushing the complete reviewed
fix/test set; the unrelated PDF remains excluded.

## 2026-11-03 — Documentation verification

Reviewed all 22 tracked Markdown files against the current Python CLI/package,
spatial validators/server, browser navigation/media/rendering, demo/fixture
producers and pinned frontend dependency manifests.

- README now lists every command/option, media selection precedence, notes and
  source handling, supported annotation semantics, recent fixes, spatial
  features and documentation entry points.
- The spatial guide now documents the implemented sidecar schema with a usable
  example, controls/path switching/backup detours, media behavior and resource
  limits. It no longer uses the broader editor/save proposal as a user manual.
- Setup instructions name Python/TeX and frontend prerequisites. The pinned
  frontend dependencies require Node 22.13+; current tools are Node 24.13.0 and
  npm 11.21.1. Developer instructions distinguish probe/dev resources from the
  built production viewer and document the installed-wheel proof prerequisites.
- Updated current status after merge and `f1db522`; removed obsolete current
  exclusions for automatic media discovery and selected LaTeX source payloads.
  Historical plans, decisions, test counts and evidence remain labelled with
  their original context. No retained evidence files were rewritten.

Verification: 64 local links/heading targets resolve; 28 shell blocks pass
`bash -n`; both JSON blocks parse; all CLI commands and non-help options appear
in README. The new layout example passes Python validation through the live
loopback server and the browser's `parseProject` validator. A temporary project
also exercises packing/inspection with assets, explicit notes, sources/output,
presenter argument passthrough, `texdir`, unchanged PDF bytes and notes excluded
from the browser surface. The unrelated example PDF's hash is unchanged.

Local receipts: `build/release-review/docs-checks.json`, `docs-smoke.json`,
`docs-browser-model.json` and the documented example's validated project JSON.
The latest published PyPI page was checked for the distinction between 1.2.0
and the unreleased checkout features. This pass changes documentation only;
the 208-test/27-frontend validation above remains the code checkpoint. No full
test suite or live pdfpc rendering was rerun for these documentation edits.
Changes are uncommitted; version/tag/publication are unchanged.

### Release cold read and documentation publication

User authorized commit/push and requested a cold read for release/PyPI readiness.
The read found one additional documentation issue: relative README links would
resolve incorrectly on PyPI. Converted its documentation links to absolute
repository URLs and added released-package installation instructions. The other
manuals retain their local navigation; dated results and retained evidence stay
in their original context.

Fresh validation: 208 Python tests, 27 frontend tests, Ruff, mypy, Poetry lock,
TypeScript/production build and isolated installed-wheel proof pass. Strict
`twine check` passes for wheel and sdist. Rebuilding a wheel from the sdist with
Node absent from PATH produces identical bytes for every wheel member (219
members), including frontend resources, notices, TeX helper and metadata.
The first rebuild check accidentally resolved the local `build/` directory as
a Python namespace instead of the absent PyPA build tool; retained the tooling
failure log and reran successfully through the existing Poetry build command.
Twine was installed in an isolated temporary environment; project dependencies
and metadata were not changed.

Readiness verdict: no remaining code/documentation blocker found within the
documented Python 3.14.4/Linux/Chromium qualification. Recommend 1.3.0 for the
new spatial route. Upload is not ready as-is: both metadata version fields still
say 1.2.0, which already exists on PyPI. The release step must bump the version,
replace pre-release availability wording and produce/check the final versioned
artifacts before tagging/upload. PyPI upload authentication was not tested;
no credentials were read and no upload/tag/release was attempted. The latest
PyPI project page and filename-reuse rules were checked against the official
site. Live pdfpc and additional Python/browser platforms were not requalified.

Local receipts: `build/release-review/cold-read-packaging.json`,
`cold-read-twine-check.log`, `cold-read-sdist-rebuild.log`,
`cold-read-frontend-tests.log` and `cold-read-installed-proof.log`.
The user-authorized documentation commit excludes the unrelated
`examples/wrapperless.pdf` and generated build artifacts.

## 2026-11-03 — Release 1.3.0

User explicitly authorized version 1.3.0, the GitHub tag and PyPI publication.
Updated both version fields and the current README/guide/status wording; the
v1 archive schema and existing route behavior remain unchanged. Release checks
and artifacts are retained under `build/release-1.3.0`, with final wheel/sdist
copied by exact filename to `dist/`. Older published artifacts and the unrelated
untracked example PDF are preserved. Publication completion will be recorded
after the tag and PyPI file hashes are verified remotely.

Final 1.3.0 validation passes: 208 Python tests, 27 frontend tests, Ruff, mypy,
Poetry lock and frontend production build; strict Twine checks; sdist rebuild
without Node with all 219 wheel members byte-identical; isolated installed-wheel
route/browser/cleanup proof. Both the installed proof and local packaging
receipt agree on the final hashes. Coverage remains 98.25% statements / 95.39%
branches. Release bytes in `dist/` match `build/release-1.3.0/packaging.json`.
Proceeding with the release commit, annotated tag and upload of the exact two
1.3.0 filenames. No source, media, PDF rendering or runtime dependency change
is part of the version bump.

Publication completed: release commit `6b0af39c94dfb608f1585b9b5d7a09349d448ae2`
and annotated tag `v1.3.0` reached GitHub. Twine uploaded exactly the 1.3.0 wheel
and sdist to PyPI. Official PyPI JSON and actual public downloads both match:

- `beamerpkg-1.3.0-py3-none-any.whl`: 2,777,101 bytes;
  SHA-256 `640b5c75a68a746b1d604b9cd8153d597700e04b30bea353b5e1fa0aac8e5641`.
- `beamerpkg-1.3.0.tar.gz`: 2,635,830 bytes;
  SHA-256 `db4477897ab20ff7d602bcc7256015ff5de687930adf0868a56d89fc8e1d4a87`.

The [public release receipt](docs/releases/1.3.0.json) binds the tag/commit,
artifact URLs/hashes, validation results and qualification limits. Credentials
were passed only through the upload subprocess environment; none was printed,
stored or hashed. This post-publication checkpoint records completion without
moving the release tag. The unrelated example PDF and earlier release files
remain untouched.
