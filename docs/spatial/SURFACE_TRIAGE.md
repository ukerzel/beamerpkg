# First-MVP surface triage

Historical classification at the 2026-11-01 S4 transition. The user subsequently
walked through the demo and authorized the merge into `main` on 2026-11-03.
The pending actions and branch boundary below describe that earlier checkpoint;
see the [current status](../NEXT_STEPS.md) for later decisions.

## Triage Scope

- Scope: the optional spatial route, adapter experiment, fixture producers and
  retained first-MVP evidence at the S4 transition.
- Sources inspected: Active Batch, first-MVP contract, current file inventory,
  ADR-001, S1/S2/S3 reports, distribution/browser receipts and tests.
- Completeness: complete by these owner groups; not a line-by-line scientific
  audit or certification of arbitrary PDFs.

## Classification Table

| Item | Type | Path | Decision | Claim Scope | User-Facing Name | Required Action | Evidence Needed | Risk If Left |
|---|---|---|---|---|---|---|---|---|
| Optional presentation route | Code/CLI | `src/beamerpkg/spatial_*.py`, frontend viewer/controllers | public_research_lane | readability | Spatial presentation (prototype) | none | S4 installed proof; human walkthrough pending | Prototype mistaken for lecture-ready parity |
| Existing package/pdfpc route | Code/tests | `package.py`, existing CLI and regression tests | canonical_framework | not_scientific | beamerpkg / pdfpc presentation | none | Existing regressions, unchanged package owner | New mode coupled to old route |
| Canvas comparison | Developer runner | `probe.html`, `src/probe.tsx`, probe tests; dev-only React Flow | developer_tool | not_scientific | none | none | Gate 0 report and ADR | Accidental second production engine |
| Fixture producers | Tool/source | `tools/build_spatial_fixtures.py`, `examples/spatial/science.tex` | developer_tool | readability | Synthetic teaching fixture | none | Actual generated PDF mapping/hashes | Synthetic bands mistaken for validated simulation |
| Installed-distribution checker | Tool | `tools/check_spatial_distribution.py`, `scripts/installed-proof.mjs` | developer_tool | not_scientific | none | none | Exact wheel selection, local dependency and browser receipts | Checkout/developer tools conceal missing runtime assets |
| Built app/resources | Generated artifact | ignored `src/beamerpkg/static/spatial/`; wheel/sdist includes | canonical_framework | not_scientific | Bundled viewer | none | Pinned build, local resources, licenses, distribution inventory | Missing offline resources or unlicensed copies |
| Reports/screenshots/receipts | Docs/artifacts | `docs/spatial/evidence/`, S1/S2/S3/evaluation | evidence_only | readability | Prototype evaluation | none | Source identities, failures and claim limits | Attractive screenshots mistaken for physical/product validation |
| Traces/packages/browser caches | Generated artifact | ignored `build/spatial-*`, `/tmp` browser/npm caches | evidence_only | not_scientific | none | none | Failure summaries and recovery paths in reports | Large transient outputs become public framework surface |
| Broader editor proposal | Design docs | `docs/SPATIAL_PLAN.md` | developer_tool | not_scientific | Spatial design roadmap | none | User decision after first-MVP walkthrough | Deferred editor/write API silently promoted into execution |

No continued unbounded spike or deletion is proposed. The comparison is a
bounded reproducible developer tool; only DOM is the production engine.
Evidence-only does not imply deletion or automatic regeneration.

## Recommended Next Action

- One action: a human walkthrough of the built fixture and an actual research
  talk, using the guide, before choosing further spatial work.
- Why this action first: the remaining product hypothesis is usefulness during
  presentation; software and screenshots cannot establish it.
- Explicit non-actions: no refactor, file movement, deletion, release, merge,
  schema change, editor or writable API is authorized by this classification.

## Stop Conditions

Stop at the first-MVP technical boundary. Preserve the branch/evidence. Further
scope needs a user decision; this triage does not authorize cleanup or promotion.
