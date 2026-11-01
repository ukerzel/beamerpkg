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
