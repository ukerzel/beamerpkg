# Spatial MVP execution

## Active Batch

SPATIAL-001: first optional spatial presentation route, on
`feat/spatial-prototype`. User authorized plan/cold-read/commit/push followed by
execution on 2026-11-01. Contract: [docs/SPATIAL_MVP.md](docs/SPATIAL_MVP.md).

Current state: **S0–S4 technically complete; stop at human walkthrough**.
No further implementation rung is active. Human presentation/product acceptance
remains pending and is not implied by software qualification.

Completed: S0 plan/cold read published in `2fa9f70`; S1 has 22 focused tests
and 41 total passing tests, Ruff/mypy passing. S1 report:
`docs/spatial/S1_REPORT.md`.
S1 published as `20bd4de`. S2 comparison passed both adapters with actual
playback and known rotated/cropped geometry; DOM selected by ADR-001.
Gate 0 evidence is in `docs/spatial/GATE0_REPORT.md`.
S2 published as `1b41ff0`; S3 has 57 Python tests and 18 frontend tests passing,
plus static/build checks. Report: `docs/spatial/S3_REPORT.md`.
Final: 59 Python and 21 frontend tests pass. The isolated installed-wheel
proof passes without Node/npm/pdfpc on runtime PATH, with external browser
requests blocked, real media/206 responses, paused restore and private-temp
cleanup. Asset-boundary follow-up published as `af80080`; final receipt and
source hashes are in `docs/spatial/evidence/s4-20261101/distribution.json`.
Evaluation: `docs/spatial/PROTOTYPE_EVALUATION.md`; guide:
`docs/spatial/USER_GUIDE.md`. Commit/push final S4 evidence, then stop.

Proceed S0 -> S1 -> S2 -> S3 -> S4 when each exit passes. Retain failed
evidence and stop at the contract's material boundaries. No full editor,
release, merge to main, or new package schema. Both existing and spatial routes
remain independent; each talk may use one or both.

Ownership: parent agent implements the scoped Python modules, frontend,
fixtures/tests, and documentation. No delegated work is authorized or required.

Follow-up 2026-11-02 (user request, not yet committed): "wow" presentation
pass on the viewer (see `docs/MVP.md`, presentation polish). 59 Python and 22
frontend tests pass. Human rehearsal still pending.
Follow-up 2026-11-02: the pdfpc demo talk gained a generated spatial layout
(`tools/demo_spatial_layout.py`, tour + deck paths); see `docs/MVP.md`.

## Deferred

- Full graphical editor, writable persistence API, archive-contained layouts.
- Presenter notes/timer/next preview, dual monitor, broader OS/browser matrix.
- Human lecture rehearsal and audience-orientation decision after S4 evidence.
