# First-MVP cold read and hardening — 2026-11-01

This is a separate self-review of the draft, not an independent review.
Scope: [SPATIAL_MVP.md](../SPATIAL_MVP.md), the broader spatial plan, current
package/CLI boundaries, and real demo annotations observed in feasibility review.
No browser or product acceptance is asserted here.

## Scientific Plan Hardening

Scope:
- New presentation workflow and evidence-producing rendering/media tests.
- No physical model, numerical reconstruction, or instrument claim. The
  physical-model checklist is inapplicable because PDF content is not altered.
- Coordinates, appearance, resource limits, comparative evidence and human
  interpretation do apply. Timing is diagnostic, geometry is correctness, and
  buffer estimates are not total browser memory.

Accept / Modify / Reject / Defer:

| Item | Decision | Reason | Required plan/issue change |
|---|---|---|---|
| Alternative pdfpc/spatial routes | Accept | User chooses per talk; no replacement | Route-isolation tests; no spatial imports in old commands |
| Full editor in first MVP | Defer | Too much work before navigation value is tested | Read-only adjacent JSON, no PUT/save endpoint; broader milestone remains incomplete |
| Implicit approval at every passing gate | Modify | User now explicitly authorized working through ladder | Automatic S0–S4 progression, stop at named failures; no merge/release |
| Preflight followed by reading original archive | Modify | Replacement between checks could bypass admission | Validate/extract a private admitted copy |
| XML/TeX inference of frame groups | Reject | Can silently attach overlays to wrong frame | Explicit grouping, exact PDF hash and compatible geometry |
| Media deduplication | Modify | One asset can have multiple policies/placements | Per-annotation inventory and per-object runtime identity |
| Pixel parity / lecture-ready claim | Reject | Different renderer; no human rehearsal | Appearance inspection and provenance; human acceptance pending |
| Unbounded rendering / archive processing | Modify | Current validator is eager; large canvases grow quadratically | Freeze numeric bounds before benchmark; bounded actual reads/cache |
| Adapter comparison | Accept | Library decision should use actual PDFs/media | Same workload, installed versions, honest timing/memory/continuity evidence |
| Live pdfpc check | Modify | Desktop interaction may not be available headlessly | Keep historical evidence; label subprocess tests as software-only |

Required Amendments:
- Make first MVP explicitly smaller than the broader editor milestone.
- Keep sidecar binding and runtime validation on both server and browser.
- Include offline ancillary PDF.js resources and fresh wheel/sdist checks.
- Specify nested history, resize, media lifetime, blocked-play and hidden-tab
  controls; distinguish injected failures from real playback.
- Add scoped contributor authority before any UI or spatial behavior.

Stop Conditions Before Coding:
- The reviewed plan must be committed and pushed before S1.
- No scientific target or unresolved physical formula is involved. No new
  human-selected scientific threshold is needed; budgets are engineering bounds.
- Missing upstream configuration blocks push, not a reason to alter Git policy.

Proceed?
- Yes, with Active Batch S0 publication, then S1 if publication succeeds.
- Human readability/product acceptance remains a separate observation at S4.

## Error-exposing questions

1. Could the old presenter fail because an adjacent spatial sidecar is stale?
   It must never read that sidecar; test the old command with invalid JSON.
2. Could a camera move remount a video and still pass screenshot checks?
   Yes. Require element identity and advancing currentTime during real playback.
3. Could a repeated-page benchmark be mistaken for real research evidence?
   Yes. Label repeated-content stress separately from the compiled science
   fixture and leave audience-orientation claims to human evaluation.
4. Could byte limits be applied too late, or bypassed by replacing the archive?
   Yes. Bound actual reads before eager inspection, then use a private copy.
5. Could an attractive viewer count as the full v0.3 implementation?
   No. This first MVP defers the graphical editor/write API explicitly and
   records its own technical acceptance and remaining limitations.
