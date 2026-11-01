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
