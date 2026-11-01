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
