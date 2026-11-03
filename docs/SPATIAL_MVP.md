# First spatial MVP: read-only presentation slice

Date: 2026-11-01. Branch: `feat/spatial-prototype`.
Status (2026-11-03): merged into `main` at the user's instruction after the
user's walkthrough. The no-merge limits below describe the ladder as authorized
at the time; they are kept as history.
Baseline: `2e86c6f3be328f6c55d42ac0d792084d1372e95d` (package 1.2.0).

This is the executable first slice of [the spatial design](SPATIAL_PLAN.md).
It proves a usable presentation route before investing in a graphical editor.
It does not claim completion of the broader v0.3 editor/save milestone.

## Outcome and boundaries

Run `beamerpkg spatial talk.beamerpkg` to view the original PDF on a spatial
canvas through locally bundled PDF.js. Use a conservative default layout or
a validated adjacent `talk.spatial.json`. A hand-authored sidecar can group
consecutive overlays, place frames, define whole-frame/detail/overview targets,
and order a presentation path. Advance overlays in place, explore, and return.
Both existing video annotation forms must play within their PDF rectangles.

The existing `pack`, `inspect`, and `present` route retains its behavior and
does not import spatial modules or inspect a spatial sidecar. Spatial launch
does not require pdfpc. Each talk may use either route or both.

This MVP reads sidecars and never writes them. No editor, save endpoint,
source conversion, arbitrary PDF actions, transcoding, presenter notes/timer,
dual-monitor support, archive migration, release, or merge to `main` is included.
Manual JSON preparation is an explicit limitation. Full editor/save support
remains a later milestone in the broader plan.

PDF bytes, media paths, and container schema v1 remain unchanged. PDF.js is a
separate renderer, so qualify appearance instead of promising identical pixels.
Scientific images remain existing raster/vector PDF content; no reconstruction,
measurement, scientific correction, or new physical claim is made.

## Authority and sequencing

The user's 2026-11-01 instruction authorizes planning, cold reading,
commit/push, and execution through this first-MVP ladder on the feature branch.
Publish the reviewed plan before implementation. Record and commit each passing
rung, then proceed automatically within this ladder. Existing design wording
requiring review at every gate is superseded for these rungs only. Stop for a
material failure or a scope change listed below; do not weaken a gate to pass.

`issues.md` Active Batch records the current rung. `TASK_STATE.md` records
handoff-critical evidence and the next action. No release, PR merge, changes
to `main`, full editor, or broader v0.3 execution is authorized by this ladder.

## Contracts

- Coordinates: PDF user space -> actual per-page PDF.js viewport -> normalized
  top-left rectangle -> object/world coordinates -> camera. Zero-based page
  indices; finite positive rectangle extents; no page grouping across unequal
  viewport geometry. Compare transformed corners within 1 CSS pixel.
- Sidecar: format `beamerpkg-spatial`, schema 1, exact PDF SHA-256/path binding;
  distinct frame/object/viewpoint/path-step IDs; references/ranges validated in
  Python and browser runtime. Reject non-finite values, unknown fields/enums,
  duplicate keys/IDs, invalid geometry, overlapping/nonconsecutive groups, and
  stale hashes. No inferred overlays or automatic rebase. The default import
  never overwrites a missing or invalid authored layout.
- Navigation: `all` visits overlays symmetrically before changing step;
  `fixed` uses its index (default 0). Overlay updates never move the camera.
  Escape pops one detour; presentation arrows in exploration restore the guided
  anchor without advancing. Overview is silent. A resize preserves world
  center/scale for runtime restoration; semantic targets refit on new entry.
  Reduced-motion uses instant transitions; interrupted animation cannot snap back.
- Media: inventory identity includes PDF/page/annotation/path; runtime identity
  adds canvas object. Same-instance camera/detail changes preserve element/time.
  Object/page/placement exit, overview, or hidden tab pauses immediately. History
  restores saved time paused; tab return does not autoplay. Deliberate autostart
  entry restarts from zero; click-to-play retains per-instance position. Unknown
  annotation flags stay unknown; controls/loop follow encoded fields. Catch play
  rejection visibly, expose decode errors, and allow only one audible stream.
- HTTP: ephemeral port on `127.0.0.1`; validate Host and supplied Origin;
  GET/HEAD only; exact static/runtime allowlists, no source/notes tree exposure,
  no arbitrary path endpoint, no directory listing, no CORS or executable actions.
  Single byte ranges support suffix/open/closed ranges, 200/206/416, correct
  lengths and HEAD behavior. Keep temporary extraction alive until Ctrl+C.
- Distribution: pinned frontend lockfile and licenses; bundled worker and needed
  fonts/CMaps/ICC/WASM. End users need no Node or online fetches. A fresh wheel
  and sdist must contain usable built assets. No new Python runtime dependency.

Predeclared engineering bounds for this slice (not scientific thresholds):

| Resource | Limit / response |
|---|---|
| Archive bytes | 512 MiB before ZIP open |
| ZIP entries | 4,096; reject duplicates and symlinks |
| Expanded bytes | 256 MiB per entry; 1 GiB total; ratio <= 200 |
| Manifest | 1 MiB; bounded actual reads before existing validation |
| Sidecar | 512 KiB; bounded reads; reject invalid UTF-8/JSON |
| PDF pages / objects / viewpoints / path steps | 200 / 400 / 800 / 2,000 total |
| Absolute world coordinate / object width | 1,000,000 / 100,000 units |
| Detour stack | 32; reject further detours visibly rather than lose resume point |
| Retained canvas buffers | 128 MiB; 16 million pixels per surface, max dimension 8,192 |
| Render work | One PDF render at a time; 320px overview thumbnails; bounded active surfaces |

Validate ZIP metadata and actual decompressed byte counts before calling the
existing eager validator. Use a private admitted copy so the archive cannot be
replaced between preflight and validation. Existing package/CLI behavior is not
rewritten. Performance timings are diagnostic: report startup, render latency,
camera responsiveness, memory estimate, and media remount count with hardware,
browser, viewport, DPR, fixture hash, and cold/warm state. Do not claim FPS,
total process memory, or superior audience orientation from buffer accounting.

## Execution ladder

| Rung | Owned implementation / evidence | Exit and next action |
|---|---|---|
| S0: reviewed plan | This contract, cold read, scoped `AGENTS.md`/`REVIEWING.md`/`docs/MVP.md` addenda; Active Batch | Cold-read gaps amended; baseline tests/static checks; commit/push plan. Then S1. |
| S1: media and admission | `spatial_project.py`, per-annotation API alongside existing discovery, `spatial_model.py`; focused Python tests | Real demo inventory, bounded ZIP admission/sidecar validation, malformed/unsafe controls, old discovery API unchanged. Full Python/static checks; commit/push. Then S2. |
| S2: browser feasibility | `frontend/spatial/` pinned dependencies; bounded comparison harness; `docs/spatial/GATE0_REPORT.md` and ADR | Same 30–50-page workload with both adapters, cropped/rotated geometry, real math/poster/media. Verify media continuity and offline resources; choose adapter from evidence. Stop if essential appearance/geometry/media cannot work. Commit/push; then S3. |
| S3: usable viewer | Read-only `spatial_server.py`, opt-in CLI, selected adapter, navigation/render/media controllers; browser/state/HTTP tests | Guided group/detail/detour/restore and both videos work; read-only boundary/Range/route isolation pass. No full editor. Commit/push; then S4. |
| S4: installed-wheel proof | Reproducible compiled scientific fixture/layout builder, relocation/offline wheel+sdist checks, README and evaluation | Full relevant suites/static checks; screenshots and machine evidence; pdfpc passthrough regressions intact; commit/push evidence. Stop with human walkthrough instructions and residual limitations. |

S2 is the broader plan's Gate 0 feasibility decision. S3 covers its read-only
guided/video behavior. The broader Gate 3 editor/write API is deferred.
S4 is technical qualification, not an assertion that a person has rehearsed a
lecture or that spatial navigation improves audience comprehension. Human
readability/product acceptance remains explicitly pending until actually observed.

## Evidence and controls

Use fresh `examples/demo.tex` and `examples/wrapperless.tex` builds and a small
compiled scientific fixture: three overlays, equations/vector drawing, an image,
region targets, nearby results, both media forms. Record page mapping and hashes
from actual outputs. A 30–50-page workload can repeat real pages for stress only;
label it repeated-content stress, not a representative research talk.

Positive controls: overlay symmetry, exact source bytes after relocation,
two placements referencing one asset, repeat/controls in standard `/Movie /A`,
pdfpc query flags, MP4 seek and advancing currentTime, independent duplicate
objects, same-instance detail changes, resize, interrupted navigation.

Negative controls: stale/invalid sidecar, missing/remote/traversing asset,
nonfinite/missing rectangle, unsafe launch, wrong Host/Origin, unsupported HTTP
method, empty/out-of-range/multiple ranges, ZIP bomb limits, hidden-tab pause,
blocked autoplay, malformed flags, unsupported decode, browser/pdfpc absence.
Use a fake presenter only to verify argument order and extraction; it does not
establish live pdfpc rendering. No browser security/autoplay overrides or silent
muting may manufacture media acceptance. Synthetic error injection is reported
separately from actual browser playback evidence.

Retain reproducible fixture producers and acceptance tests. Reports describe
commands, versions, source identities, results, failures and limitations; saved
screenshots may be reviewed visually but do not prove pixel parity. Keep large
generated packages/video copies/browser binaries/node_modules outside Git.
Archive immutable small evidence under a named run; never overwrite a failed
result and call its replacement the original. Bound the adapter comparison
as developer evidence; only the selected engine becomes production code.

## Stops and rollback

Stop if essential PDF content fails without a scoped fix; annotations cannot
be placed reliably; active audio cannot be stopped; source bytes/paths or
existing command behavior would change; browser tooling cannot be obtained;
or a custom renderer, schema change, source exporter, transcoder, write API,
or major dependency is needed. Diagnose narrowly and retain the failure.

Ordinary failing tests within the accepted contract are implementation work,
not a reason to abandon the ladder. Do not skip tests, silently substitute
fake media for real playback, change budgets after seeing results, or claim
human acceptance. Preserve branch commits and return to `main` only if asked;
no reset/revert/clean or automatic feature-branch deletion.

## Technical references

- [PDF.js examples](https://mozilla.github.io/pdf.js/examples/) and
  [loading resources](https://mozilla.github.io/pdf.js/api/draft/module-pdfjsLib.html).
- [React Flow camera APIs](https://reactflow.dev/api-reference/types/react-flow-instance).
- [Media play rejection](https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement/play).
- [Playwright browser testing](https://playwright.dev/docs/intro).

Pin and inspect installed APIs in S2; these references explain the design, not
evidence that the implementation has passed.
