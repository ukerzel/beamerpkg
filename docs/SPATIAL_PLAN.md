# beamerpkg Spatial v0.3 — Optional Presentation Route & Codex Handover

**Status:** Broader design; the first read-only MVP is now authorized through S0–S4 in [SPATIAL_MVP.md](SPATIAL_MVP.md). Full editor/save scope remains deferred.

**Date:** 2026-11-01

**Repository:** https://github.com/ukerzel/beamerpkg (`main`, observed `pyproject.toml` version **1.2.0**)

**Supersedes:** `/home/kerzel/beamerpkg_spatial_v0_2_codex_handover.md` for future planning. Preserve that handover and `beamerpkg_spatial_v0_1_spec.md` as history.

**Version meaning:** v0.3 identifies this spatial plan/prototype milestone. The existing Python package remains 1.2.0; container schema v1 and illustrative spatial sidecar schema v1 are unchanged by this document.

**Audience:** Codex / developer implementing the first technical prototype.

**Goal:** Add an optional spatial navigation and presentation route for scientific Beamer material, with restrained camera movement, readable PDF content, and packaged-video functionality. The existing pdfpc route remains supported in its own right. Authors choose pdfpc, spatial, or both for each talk; no talk needs to be prepared or qualified for both routes. Spatial mode uses the original PDF rather than re-typesetting LaTeX.

> **Execution authority:** The user's 2026-11-01 instruction authorizes planning, cold read, commit/push, and execution through the first-MVP ladder in [SPATIAL_MVP.md](SPATIAL_MVP.md). That contract and `issues.md` Active Batch govern this first slice and supersede review-at-every-gate wording below for S0–S4 only. Keep `pack`, `inspect`, and `present`/pdfpc independent of spatial metadata, a browser, or Node. Spatial launch needs no pdfpc. The broader graphical editor/save API, deployment, release, and merge remain outside this authorization.

---

## 0. Revision decisions (v0.2 → v0.3)

The user clarified that spatial development is an alternative to the existing workflow. Each talk may use either route or both. The following decisions amend the previous handover:

- Preserve pdfpc as a supported route with its own acceptance criteria and no planned replacement or deprecation.
- Keep presenter selection explicit and isolate route-specific metadata, dependencies, errors, and readiness decisions.
- Require dual-route regression fixtures at project level, without imposing two presentation versions on every talk.
- Make PDF.js fidelity, render budgets, media activation/restore, offline resources, and pre-validation archive limits explicit.
- Move scope documentation to the start of a future authorized Gate 0. Do not interpret this planning revision as implementation authority.

The earlier object-model corrections remain applicable:

The earlier handover was directionally sound, but its object model and build order could accidentally recreate discontinuous slide jumps and allow a technically functioning demo that cannot preserve scientific presentation behavior.

| Priority | Change | Reason |
|---|---|---|
| P0 | A **frame source** is the canvas content unit; explicit groups collect its overlay pages. Conservative import creates single-page sources until grouping is supplied. | Beamer overlays must change in place, without camera jumps or guessed grouping. |
| P0 | Distinguish **content source / canvas object / viewpoint / path step / navigation history**. | An object can be viewed repeatedly at different scales without being duplicated. |
| P0 | Build a real **navigation state machine**. | Guided progression, free exploration, overview, and return must be deterministic. |
| P0 | Create a central **media controller** and explicit media-discovery inventory. | Video must stay aligned, avoid restart on zoom and always stop sound on exit. |
| P0 | Specify **local-sidecar persistence API** and write security. | A web editor cannot automatically save arbitrary local files. |
| P0 | Add **Gate 0 feasibility**, comparing React Flow with a simpler transform canvas before committing. | Main uncertainty is large scientific PDF rendering + media, not basic diagram drawing. |
| P1 | Test **scientific PDF fidelity** and real compiled movie annotations, not synthetic rectangles alone. | Beamer equations, vector graphics, crop/rotation, and media semantics are core value. |
| P1 | Distinguish **technical prototype** from **lecture-ready presenter**. | Speaker view, timers, notes and cross-platform reliability are not in v0.3. |
| P1 | Update repo scope/contributor guidance explicitly. | Current `AGENTS.md` still forbids GUI/HTML rendering as part of the original MVP. |
| P1 | Validate precise PDF.js and React Flow APIs against pinned versions. | In 2026, PDF.js removed `convertToViewportRectangle`; use point conversion. |

## 1. Product hypothesis and demonstration

### Hypothesis

For a scientific talk, keeping an understandable *spatial context*—overview, simulation, experiment, analysis, and subregions—improves orientation and question-driven exploration over abrupt jumps between unrelated PDF pages. The improvement must come from meaningful spatial organization, not theatrical camera effects.

### Per-talk route choice and compatibility

| Author's choice | Preparation and launch | Required qualification |
|---|---|---|
| pdfpc only | Existing `.beamerpkg`; `beamerpkg present talk.beamerpkg` | Existing container and pdfpc contract. No spatial sidecar, browser, or frontend authoring required. |
| Spatial only | Same v1 container as content input; `beamerpkg spatial talk.beamerpkg`; save layout when useful | Spatial rendering, navigation, and media used by this talk. pdfpc installation, a separately designed linear talk, and pdfpc rehearsal are not required. |
| Both | One v1 archive with an optional adjacent `talk.spatial.json`; choose the command explicitly | Qualify each route for the features used there. Shared PDF/media bytes do not imply identical navigation, playback policy, or presenter features. |

These are authoring and use choices, not new package types or manifest flags. `pack` and `inspect` remain route-neutral. A spatial-only talk still uses a PDF and v1 container; it does not require an additional input format. The initial default grid works without a sidecar, but a deliberately authored spatial arrangement needs one for reuse.

A spatial path may select, reorder, revisit, or show details of PDF frames independently of the PDF's linear page sequence. The author need not produce matching presentation orders. Shared PDF/media content must remain untouched by layout edits.

A missing, invalid, or stale spatial sidecar must not affect `pack`, `inspect`, or `present`. Those commands do not read or create spatial metadata. Failure in the spatial route produces a spatial-specific error; it never automatically starts pdfpc. Conversely, `present` always launches the configured native presenter and never automatically opens spatial mode.

### Concrete demo story

Use the committed multimedia demo for feature/regression tests. In addition, create a small **scientific** test canvas (an existing research deck if available, otherwise a synthetic Beamer research fixture):

1. View an overview of a simulation → experiment → analysis workflow.
2. Focus the scattering-model frame; step through 3 Beamer overlays **in the same spatial rectangle**.
3. Zoom into an equation or specific Kikuchi band as a named viewpoint; return without losing the preceding overlay state.
4. Move smoothly to a nearby experimental-pattern/results object.
5. Detour to a supplementary result during Q&A; one action returns to the prior planned step.
6. Open the video frame, play packaged media, pan/zoom while playing, and leave with audio stopped.

A mere grid of PDF thumbnails with animated page transitions is **not sufficient evidence** for the product hypothesis.

### Technical v0.3 success vs. product readiness

- **Technical prototype:** correct frame grouping, camera paths, exploration/restore, real PDF rendering, both packaged video modes, offline launch, edit/save/reload, automated checks, untouched pdfpc path.
- **Readiness for a spatial talk:** assess the features that talk and presenter actually need. Notes, timers, next-preview, dual-monitor support, remotes, broader browser/OS coverage, and archive-contained layouts are possible later milestones; none is automatically required to replace or match pdfpc. A talk needing an unavailable spatial feature continues to use pdfpc if its author chooses that route. pdfpc remains independently supported even if spatial mode becomes lecture-ready.

## 2. Existing code and boundaries (verified against repository)

| Repository path | Current behavior and action |
|---|---|
| `src/beamerpkg/package.py` | `SCHEMA_VERSION = 1`; `pack_package`, `inspect_package`, `extract_package`; ZIP members checked by hash/size, paths constrained. **Reuse v1 semantics.** Add spatial-launch archive resource preflight before validation reads; do not change the package schema or existing command behavior. |
| `src/beamerpkg/pdf_media.py` | `discover_pdf_media_references()` extracts/deduplicates paths for `/Movie` and recognized pdfpc `/Link` + `/Launch`. **Retain API**; add a per-annotation placement API alongside it. |
| `src/beamerpkg/cli.py` | Existing `present` launches pdfpc with passthrough arguments. **Add a separate `spatial` subcommand**; do not alter passthrough. |
| `src/beamerpkg/tex/beamerpkg.sty` | Stock `\movie` compatibility and pdfpc-specific `\pkgpdfpcmovie[autostart&loop]`. **Do not require new macros** to use spatial mode. |
| `examples/demo.tex` / `examples/build_demo.sh` | Compiles demo with overlays and two media slides referencing the same MP4. Mandatory real compiled end-to-end fixture. |
| `examples/wrapperless.tex` | Standard `\movie` test without a beamerpkg-specific macro. |
| `examples/demo.pdfpc` | pdfpc notes sidecar, retained unchanged for the existing route and its regressions. Spatial notes support is a separate future choice. |
| `tests/test_package.py`, `tests/test_cli.py` | Existing synthetic annotation, packaging and CLI tests. Extend; do not remove. |
| `AGENTS.md`, `REVIEWING.md`, `docs/MVP.md`, `docs/NEXT_STEPS.md` | Primarily describe the historical packaging MVP; some exclusions are already outdated. At the start of separately authorized Gate 0, append the concrete spatial requirement to `docs/MVP.md`, add `docs/SPATIAL_MVP.md`, and add narrow `AGENTS.md` / review guidance addenda **before UI prototypes or new spatial behavior**. Preserve the historical MVP and existing-route acceptance criteria. This planning document alone does not amend those instructions. |

### Invariants

1. **Ordinary Beamer → ordinary PDF** continues to compile and present through pdfpc without modification.
2. Existing v1 `.beamerpkg` archives continue to validate with `inspect` and launch with `present`.
3. v0.3 spatial layout resides in an **adjacent sidecar** (`talk.spatial.json`), *not* in `manifest.json`. Do **not** bump package schema for this prototype.
4. Preserve PDF bytes and LaTeX typesetting. Spatial mode uses PDF.js as an additional renderer and HTML5 video as an overlay; pdfpc keeps its existing rendering route. Scientific appearance and geometry require qualification; identical pixels and all PDF annotation/transition behaviors are not promised.
5. No online service, CDN, untrusted external scripts, account, or remote content. Static application assets bundle locally.
6. Unexpected or unsupported spatial features fail visibly within that route. Existing pdfpc use remains independent; do not automatically switch presenters or require a pdfpc-compatible version of each spatial talk.
7. Retain Poetry / Python >=3.11 / pytest / type hints / Ruff / mypy conventions. Use TDD for behavioral changes and document external architectural references.
8. pdfpc remains supported without spatial preparation or frontend tools. Spatial runtime needs a supported browser and bundled assets, but no pdfpc or end-user Node installation. Import and initialize route-specific code only when that route is selected.

## 3. Architecture at a glance

```text
ordinary Beamer PDF + optional media
                 |
                 v
        .beamerpkg v1 container
                 |
      explicit CLI route choice
        /                  \
       v                    v
present                 spatial
validate/extract        resource preflight -> validate/extract
pdfpc                   local browser + optional spatial sidecar
(existing route)        (additional route)
```

The spatial branch is:

```text
existing .beamerpkg (v1, unchanged)
      |
      v
Python: bounded archive preflight -> extract_package -> verified asset inventory
      |                                |
      +--> rich PDF media inventory    +--> temporary verified files
      |                                |
      v                                v
127.0.0.1 loopback HTTP: bundled SPA / PDF / media / JSON API
      |
      v
TypeScript viewer
   - document model: frames + canvas objects + viewpoints + paths
   - PDF.js page renderer (scalable thumbnails and active surfaces)
   - selected canvas adapter (React Flow or minimal DOM transform)
   - navigation controller (guided / exploring / overview / restore)
   - central media controller + stable HTML5 video overlay
   - basic editor and validated sidecar persistence
      |
      v
<archive stem>.spatial.json  (outside archive, local prototype only)
```

The backend never generates HTML for equations, changes PDF content, starts executable PDF `/Launch` targets, or tries to replicate pdfpc's full speaker-view UI in the first milestone.

### Candidate frontend

- TypeScript + React in strict mode.
- PDF.js (locally bundled worker included).
- **Candidate A:** `@xyflow/react` (React Flow) for spatial node movement and camera APIs.
- **Candidate B:** simple absolute-positioned DOM surfaces under one `transform: translate(...) scale(...)` viewport plus custom pointer handlers.
- HTML5 `<video>` rather than a custom decoder.
- Unit tests + Playwright real-browser smoke tests.

**Architecture is deliberately not fixed before Gate 0.** React Flow's node/edge machinery and keybindings may impose costs or conflicts for an almost-edge-free PDF presentation. Choose empirically; record a short ADR.

## 4. Domain model: five concepts, explicit identities

**A. Content source (`FrameSource`)**

A logical Beamer frame and its successive *physical* PDF pages. A frame can contain one page (no overlays) or `[7,8,9]` (three overlay states). Identified by stable `frame_id`; page indices are zero-based.

**B. Canvas object (`CanvasObject`)**

A spatial placement of a source on the world canvas (`x`, `y`, width; height derived from PDF geometry or explicitly stored with aspect preservation). Multiple objects **may** reference one source if the author deliberately duplicates placement, but multiple viewpoints of one object do not duplicate it.

**C. Viewpoint (`Viewpoint`)**

A target bounding rectangle either (i) relative to one canvas object / a normalized PDF subregion, or (ii) in world-space, covering several objects (overview). Overlay entry policy belongs to the path step; v0.3 does not add a second initial-overlay field on viewpoints. Optional camera padding. Viewpoints are semantic targets, **not** persisted pixel-space pan/zoom transforms.

**D. Presentation path (`PresentationPath`)**

Named ordered steps referencing viewpoint IDs. A step specifies overlay behavior: `all` (advance overlays in place before leaving step) or `fixed` (show one chosen overlay state). The same viewpoint can appear in different paths or repeated within a path.

**E. Navigation state/history (runtime only)**

Selected path and step, overlay state keyed by canvas object ID, active object/media instance, camera pose, media time, and a bounded stack of temporary detours. Source pages are shared immutable content; duplicate canvas objects have independent runtime overlay and playback positions. **Do not persist exploration history as authoring metadata.**

### Overlay semantics (P0)

- Default import is *conservative*: each physical PDF page becomes a one-page `FrameSource` unless explicit frame grouping exists. **Never infer grouping solely from visually similar pages**; legitimate unrelated slides can look alike.
- The editor supports explicit grouping of consecutive pages into one logical frame, with preview and undo. A small hand-authored grouping fixture is sufficient for Gate 1; UI comes in Gate 3.
- Later, optional TeX-side frame grouping export may provide a reliable mapping; no new LaTeX macro requirement for v0.3.
- For a path step with `overlay_policy = all`: Right/Space moves overlay 0 → 1 → 2 **without moving the camera**, then advances to next step. Left reverses overlay 2 → 1 → 0, then moves to prior step's last state. Overlay selection is always symmetric.
- On forward entry to an `all` path step, show overlay 0. On backward entry, show its last overlay. A `fixed` step shows `overlay_index`, defaulting to 0; v0.3 does not support a separate initial overlay for `all`. Temporary exploration restores the saved overlay for every affected object. A newly encountered object starts at overlay 0; overview displays the retained per-object overlays and starts no media.
- Frame grouping includes physical pages only, not arbitrary PDF annotations. A video placement belongs to a **specific physical page**; the active placement changes with overlay state.
- Grouping may be rejected if page geometry/rotation makes stable alignment impossible; warn and retain separate frames. A deliberate manual alignment override is a later feature.

### Suggested sidecar model (valid *illustrative* JSON)

**Note:** PDF page numbers and hashes here are placeholders; Codex must discover actual demo page indices after compilation. No fake indices should be committed as a working fixture.

```json
{
  "format": "beamerpkg-spatial",
  "schema_version": 1,
  "source": { "pdf_sha256": "REPLACE_WITH_COMPUTED_SHA256", "pdf_path": "demo.pdf" },
  "frames": [
    { "id": "f-intro", "page_indices": [0] },
    { "id": "f-science", "page_indices": [5, 6, 7] },
    { "id": "f-video", "page_indices": [8] }
  ],
  "objects": [
    { "id": "o-intro", "frame_id": "f-intro", "x": 0, "y": 0, "width": 960 },
    { "id": "o-science", "frame_id": "f-science", "x": 1120, "y": 0, "width": 960 },
    { "id": "o-video", "frame_id": "f-video", "x": 2240, "y": 0, "width": 960 }
  ],
  "viewpoints": [
    { "id": "v-overview", "target": { "kind": "world_rect", "rect": [0, 0, 3200, 750] } },
    { "id": "v-science", "target": { "kind": "object", "object_id": "o-science", "region": [0, 0, 1, 1] } },
    { "id": "v-detail", "target": { "kind": "object", "object_id": "o-science", "region": [0.2, 0.3, 0.35, 0.3] } },
    { "id": "v-video", "target": { "kind": "object", "object_id": "o-video", "region": [0, 0, 1, 1] } }
  ],
  "paths": [
    { "id": "main", "steps": [
      { "id": "s-1", "viewpoint_id": "v-overview", "overlay_policy": "fixed" },
      { "id": "s-2", "viewpoint_id": "v-science", "overlay_policy": "all" },
      { "id": "s-3", "viewpoint_id": "v-detail", "overlay_policy": "fixed", "overlay_index": 2 },
      { "id": "s-4", "viewpoint_id": "v-video", "overlay_policy": "all" }
    ] }
  ],
  "media_overrides": []
}
```

Definitions/validation:

- `rect` of a world target = `[x,y,width,height]` in canvas units; `region` of an object target = `[x,y,width,height]` normalized to **the frame's rendered viewport**, origin top-left, all values in `[0,1]`, `width,height > 0`, `x+width <= 1`, `y+height <= 1`. For overlays of different aspect ratios, grouping should be rejected or layout must explicitly normalize them.
- Viewpoints always recompute camera pose from current window dimensions; viewport-size and DPI changes do not invalidate them. Do not save one browser's screen-pixel `transform` as the canonical authoring data.
- A world overview has no overlay-owning frame. `overlay_policy=fixed` there is a no-op, not an error; `all` requires an object frame target. `overlay_index` is only valid for object targets and `fixed` policy; validate range.
- Frame `page_indices` must be nonempty, unique, in PDF range; groups must not overlap by default. Adjacent is required for manually grouped Beamer overlays. `frame_id`, `object_id`, `viewpoint_id`, path-step ID references must resolve and be unique in their own spaces.
- Layout IDs are persisted and stable across *layout edits*. The PDF hash detects a TeX recompilation; on mismatch, **do not silently reassign pages or autoplay the wrong media**. Offer read-only inspection and an explicit repair/rebase procedure; initial implementation may require manual re-import.
- `source.pdf_path` must match the package manifest PDF path, not act as an arbitrary server-side filesystem path.
- `media_overrides` is reserved for **explicit user-supplied playback metadata** when annotation semantics are not recoverable. If implemented, key by verified `(page_index, annotation_index, normalized asset path)` and validate against the current inventory; do not blindly trust stale overrides.
- Schema needs JSON Schema or equivalent TypeScript runtime validation **and** Python validation. Malformed IDs, references, non-finite numbers, oversized collections, extreme positions, and hostile strings should be rejected or bounded.

## 5. Navigation state machine and controls

Modes: `editing`, `guided`, `exploring`, `overview`. Keep path state separate from current camera transform.

| Input | Guided | Exploring | Overview | Editing |
|---|---|---|---|---|
| Right / Space | Advance overlay; then step | Restore guided resume anchor, clear detours, do not advance | Restore prior mode; do not advance | No presentation advance; space may pan only in edit mode |
| Left | Reverse overlay; then prior step | Restore guided resume anchor, clear detours, do not advance | Restore prior mode; do not advance | Standard editor behavior |
| O | Push snapshot, show world overview | Push snapshot, show overview | No-op | Fit canvas |
| Click focus target | Push snapshot, focus target, enter exploring | Push nested snapshot, focus target | Focus chosen target; retain return snapshot | Select/edit object |
| Escape | No-op | Pop one snapshot; restore camera/path/overlay and paused media | Pop one snapshot | Clear selection / close editor overlay |
| Backspace | Optional *history back*, documented separately from Left | Pop snapshot | Pop snapshot | Undo only if editor uses standard shortcut (prefer Ctrl/Cmd+Z) |

**Implementation choice for v0.3:** Right/Left/Space in `exploring` restore the original guided resume snapshot without advancing and clear its temporary detours. `Escape` pops one snapshot, so nested exploration unwinds one level at a time. Retain a separate guided resume anchor and a bounded LIFO detour stack; reopening an overview must not overwrite that anchor. In overview, presentation arrows restore the prior mode without advancing. Guided Escape is a no-op; help has a separate visible control. If exploration began without a selected path, no guided anchor exists: presentation arrows are no-ops and a visible control offers path selection; Escape still unwinds available detours.

Snapshots store the world-space visible center and scale as well as the viewport dimensions. Restore the exact camera pose when dimensions match; after resize, preserve world center and scale and derive the new transform. Semantic viewpoint entry continues to fit its target to the current viewport. Restoring content state after a detour restores media time in a paused state; it does not restore a prior playing flag or trigger autostart.

Additional rules:

1. Navigation operations are centralized and testable as pure state transitions. Direct React components must not each implement their own keyboard rules.
2. Each camera animation is interruptible/cancelable; the latest user command wins. No stale animation may snap the camera back after an interruption. Default short transition 200–400 ms; instant mode, and honor reduced-motion preferences.
3. Changes to overlays within one frame never animate the camera. A viewpoint may target a detail region; its overlay changes occur under that same view.
4. Video activation follows the focused canvas object and its physical page/annotation instance, not viewport visibility alone. Changing only the viewpoint or camera on the same active media instance preserves playback. Overview, editing, object/page/placement change, or hidden tab deactivates and pauses it. A video thumbnail must not autoplay or make sound.
5. Keep separate presenter key commands from React Flow's built-in Space-to-pan and arrow-to-nudge behaviors. Disable conflicting canvas keyboard shortcuts in presentation mode.
6. On accidental jumps, one predictable action restores both content state and camera. Test history over multiple detours.

## 6. Coordinate and PDF fidelity contract

### PDF geometry

- The PDF and **per-page** `MediaBox/CropBox/Rotate` (and any relevant user-unit scaling) determine displayed geometry, not assumptions about a globally constant 16:9 aspect ratio.
- Python annotation inventory stores the original PDF-space `/Rect` as four finite numbers in order, after validating that a non-empty visible region can be constructed; preserve page index and annotation order.
- The browser converts both rectangle corners through **the actual page's** PDF.js viewport, then takes `min/max` in browser coordinates, normalizes by displayed viewport dimensions, and anchors the result to the corresponding PDF page surface. Crop/rotation/clipping tests are mandatory.
- **Do not use `viewport.convertToViewportRectangle`**: this was removed from PDF.js in June 2026. Use `convertToViewportPoint` for each corner. Lock a tested PDF.js package version and document the API.
- Derive a single transformation hierarchy: PDF user coordinates → PDF.js page viewport → normalized rectangle → canvas object coordinates → camera transform. Avoid mixing screen, node-local, canvas-world and PDF coordinates in one API.

### Rendering scope

PDF.js renders existing PDF drawing instructions; it is a separate rendering engine from pdfpc. Acceptance means legible scientific content, correct geometry, stable overlays, and documented fixture-specific differences. Do not require pixel-identical antialiasing between engines. Define visual comparison tolerances and inspect missing glyphs, shifted labels, clipping, transparency, and colors.

PDF `/Trans` transitions, arbitrary links/actions, and embedded presenter-note behavior are not implicitly supported by spatial mode. The spatial camera supplies its navigation transitions. Keep hidden notes and executable actions out of the audience surface. Existing pdfpc behavior remains unchanged. Zooming an embedded raster micrograph magnifies its existing pixels; it cannot create additional scientific detail.

### Render quality and performance

- Show low/medium-resolution page thumbnails at overview scale. Render the active view at appropriate device-pixel ratio with PDF.js; on settled zoom increase resolution or render a cropped focus region instead of stretching bitmap indefinitely.
- Limit high-resolution render cache and memory; cancel obsolete PDF.js render tasks after fast camera movement. Keep page image, annotations, and media overlay aligned throughout the transition.
- Gate 0 must record numeric limits for retained canvas bytes, canvas dimensions/pixels, render concurrency, and supported zoom on the reference hardware. A 1920×1080 CSS page at DPR 2 needs about 31.6 MiB of RGBA storage; fifty such surfaces need about 1.54 GiB before decoded images and other overhead. Retain thumbnails for overview, bound active surfaces, and render a clipped region when a full-page detail render would exceed budget. Do not silently omit content to meet limits; display a clear quality/zoom limitation when necessary.
- Test dense math glyphs, vector TikZ, high-resolution microscopy images, transparent figures, rotated/cropped pages, and browser resize; compare with PDF rendered in pdfpc or a trusted desktop PDF viewer.
- Baseline with ~30–50 physical PDF pages and at least one video. Report page count, viewport size, browser/OS, memory behavior, and subjective navigation lag. **Do not promise** an arbitrary frame rate without measurement; no blank flashes or prolonged blur should occur on planned viewpoints.

## 7. Media integration — mandatory, no shortcut

### Real existing fixtures

`examples/demo.tex` already contains:

- Standard `\movie[loop,showcontrols]` on the **“Click to play”** frame;
- pdfpc-specific `\pkgpdfpcmovie[autostart&loop]` on **“Autoplay and loop”**;
- both referencing `media/gemini_generated_video_b2693757.mp4` and poster `media/video-poster_big.png`.

`examples/wrapperless.tex` verifies ordinary stock Beamer without package macros. `examples/build_demo.sh` creates the actual bundles.

### Mandatory Gate 0 observation

Compile the **actual** demo, then emit an evidence table showing for each media annotation:

- physical page index, annotation index, `/Subtype`, `/Rect`, normalized asset path;
- `/Movie` dictionary or pdfpc `/Launch` action representation;
- options that are *actually* recoverable from the PDF (especially autostart, loop, controls);
- whether the PDF poster is rendered automatically by PDF.js or needs explicit overlay masking;
- any missing or unexpected semantics, plus a proposed explicit override when necessary.

Do **not** assume that the `loop` or `showcontrols` options in the original TeX survive identically in a compiled PDF. Do not reverse-engineer playback state from the source unless introducing an explicitly optional source-side metadata exporter for a later release.

### Preliminary feasibility observations (2026-11-01; not Gate 0 acceptance)

A review rebuilt the unchanged demo and wrapperless TeX twice each into a temporary directory and inspected annotations with pypdf. The demo had 26 physical pages; wrapperless had one. The existing Python suite passed 19 tests. These observations support feasibility but do not establish browser behavior or performance.

| Fixture | Zero-based page / annotation index | Encoded placement and playback metadata |
|---|---|---|
| Demo standard movie | 17 / 0 | `/Rect [193.231, 46.466, 424.201, 176.453]`; `/Movie /F`; annotation `/A` contains `/Mode /Repeat` and `/ShowControls true`. |
| Demo pdfpc launch | 18 / 1 | `/Rect [94.247, 46.792, 359.296, 196.82]`; `/Launch /F` ends with `?autostart&loop`. |
| Wrapperless standard movie | 0 / 0 | `/Rect [72, 35.867, 381.543, 210.079]`; `/Movie /F`; annotation `/A` contains `/Mode /Repeat` and `/ShowControls true`. |

All three reference `media/gemini_generated_video_b2693757.mp4`. Standard movie repeat/controls are encoded in the annotation's `/A` dictionary, not just its `/Movie` dictionary. Fields absent from the PDF remain unknown unless a documented PDF default is deliberately implemented. Recompute indices and geometry for implementation fixtures and record PDF hashes/tool versions in Gate 0 evidence. PDF.js poster appearance, rotated/cropped alignment, browser codecs, autoplay, and performance remain unverified.

### Python discovery API (suggestion)

Keep `discover_pdf_media_references(pdf: Path) -> tuple[str, ...]` unchanged. Add per-annotation records, *without deduplication*:

```python
@dataclass(frozen=True)
class MediaPlacement:
    page_index: int
    annotation_index: int
    asset_path: str                         # validated package-relative path
    rect_pdf: tuple[float, float, float, float]
    kind: Literal["movie", "pdfpc_launch"]
    autostart: bool | None                  # None when unknown
    loop: bool | None
    controls: bool | None
```

- Distinguish `False` from `None` (explicitly disabled vs not encoded).
- Verify every asset against the **validated package manifest inventory**. Never let `run:`/`/Launch` execute anything; recognize known media paths/options only.
- Two annotations can reference the same MP4 with different rectangles or policies: deduplication is appropriate for packaging assets, **not** for playback placement.
- Missing `/Rect`, nonnumeric geometry, malformed options, unsupported URL/absolute/escaping path: return a clear unsupported-placement result or fail closed. Never create a fullscreen media rectangle as a silent fallback.
- Normalize paths only after reference validation; do not allow `..`, symlink escapes or arbitrary protocol URLs.

### Central media controller

Use one authoritative controller. An inventory placement is identified by PDF hash, page index, annotation index, and verified asset path; a runtime instance additionally includes canvas object ID. Two objects showing one source retain separate runtime state and cannot overwrite each other's saved position. Reusing an inactive media element is allowed if switching instances restores the correct state; moving the current instance's camera must not remount it. The controller manages `idle`, `loading`, `ready`, `playing`, `paused`, `blocked`, `error`, plus current time, current asset, user-initiated state, and error message.

- Keep the actual media element stable during React rerenders, page re-resolution, and camera movement. A dedicated portal/overlay layer or stable component lifetime is acceptable; test the actual behavior rather than assuming React keys suffice.
- Position the overlay from annotation geometry in the same canvas transform as the underlying PDF page. Playback never opens a separate window, changes aspect ratio, or replaces unrelated PDF content.
- Standard `/Movie` initially displays the PDF poster and offers click-to-play. Loop/controls follow recovered settings or validated overrides; unknown flags default conservatively.
- pdfpc-autostart media: attempt play on deliberate guided entry to a newly active media instance or an explicit exploratory focus of that instance; loop if declared. Changing viewpoint within the same instance does not count as re-entry. No autoplay in editing, overview, merely visible thumbnails, history restoration, or tab visibility restoration.
- Catch `video.play()` rejection (`NotAllowedError`) and present a user-visible Play control. No silent auto-muting to bypass browser policy; no false “playing” state. Non-supported codecs get a visible error.
- Default deterministic re-entry policy: autostart media seek to `t=0` and attempt play on deliberate entry after deactivation; click-to-play retains its per-instance position within the session and waits for Play. History restore takes precedence: restore saved position paused for either kind, without autostart. Switching to another object, page, or annotation, entering overview/editing, or hiding the tab pauses immediately. Returning to a visible tab leaves media paused. A camera move, resize, or whole-frame/detail viewpoint change on the same active instance preserves time and playback.
- If a page has several placements, none becomes audible merely by being rendered. Select the single autostart-marked placement when unambiguous; if several request autostart, show a selection/Play control and start none automatically. A click on another placement pauses the old stream before activating the chosen one.
- Only **one audible media stream at a time**. When replacing a video, stop the old one before starting the new one.
- Interactive video controls must not inadvertently drag nodes or pan/zoom the canvas. For React Flow, use the supported `nodrag`, `nopan`, `nowheel` mechanisms as appropriate.
- Test URL Range requests and MP4 seeking; file serving and the media element must work fully offline.

### Media acceptance matrix

| Test | Expected |
|---|---|
| V01 | Relocated `demo.beamerpkg` loads PDF and bundled video without original build directory. |
| V02 | Stock `\movie` poster click plays in the correct annotation rectangle. |
| V03 | Zoom/pan/resize while video plays: geometry follows page; no reset/rebuffer due merely to component remount. |
| V04 | pdfpc autostart+loop: attempt on focused entry; manual Play fallback if browser blocks. |
| V05 | Changing active object/page/placement, entering overview/editing, or hiding the tab pauses sound immediately. Same-instance viewpoint changes preserve playback. |
| V06 | Deliberate re-entry applies seek/resume policy; history restore returns to saved time paused; tab return remains paused; no ghost audio. |
| V07 | `wrapperless.beamerpkg` supports the same standard `/Movie` path without a helper macro. |
| V08 | Two different annotations pointing to the same media preserve distinct page/rectangle/flags. |
| V09 | Seek within MP4 works via HTTP `206` Range with correct `Content-Range`. |
| V10 | Unsafe `/Launch`, remote URLs, missing asset, invalid `/Rect`, unsupported codec produce controlled behavior and no execution. |
| V11 | Whole-frame/detail changes on one active instance preserve playback; duplicate objects keep independent state; nested history restores content and paused media deterministically. |
| V12 | Existing `beamerpkg present examples/demo.beamerpkg` launches pdfpc unchanged and both video demo behaviors still work there. |

## 8. Local server, persistence, and security

### CLI and local lifecycle

```bash
./examples/build_demo.sh
beamerpkg spatial examples/demo.beamerpkg
# Starts a temporary server on 127.0.0.1, opens the offline viewer, loads
# examples/demo.spatial.json if present, otherwise imports a conservative layout.
# Ctrl+C stops the server and deletes the temporary extracted files.

beamerpkg present examples/demo.beamerpkg
# Still invokes the existing pdfpc workflow, unchanged.
```

- Add a separate `spatial` parser command and named Python entry function. Do not modify `present` argument passthrough behavior or `.beamerpkg` schema.
- Run a spatial-specific bounded archive preflight **before** calling existing validation/extraction: bound archive bytes, ZIP entry count, manifest bytes, per-entry expanded size, total expanded size, and compression ratio. The current `inspect_package` eagerly reads entries; a check after extraction is too late. Enforce actual byte limits during bounded reads as well as checking ZIP metadata. Freeze numeric limits and rejection tests in Gate 0. After preflight, `extract_package` remains the authority for paths and SHA-256 verification. Do not change the v1 schema or existing command behavior as part of this guard; if bounded admission cannot be achieved with that constraint, stop and review a narrowly scoped shared-validation change.
- Bind loopback `127.0.0.1` on an ephemeral port and validate the `Host` header for that endpoint. Do not bind `0.0.0.0`, expose CORS, or browse external files.
- Serve only compiled frontend files and paths listed in a validated runtime asset allowlist. Resolve symlinks and ensure containment. Disable directory listing and execution of PDF launch actions; use conservative CSP and MIME headers.
- Support `HEAD`, `GET` and single byte-range requests for MP4/PDF (`200`, `206`, `416`, `Accept-Ranges`, `Content-Range`, proper `Content-Length`). No general-purpose file browser or arbitrary filesystem URL endpoint.
- Do not expose source payload files through the browser by default. The app needs the presentation PDF and runtime assets, not the LaTeX source tree.

### Sidecar persistence contract

The sidecar lives **beside the input package**, with a deterministic archive-stem name: `examples/demo.beamerpkg` → `examples/demo.spatial.json`. It is not in the temporary extraction directory.

Transport contract for this prototype: pdfpc use requires the archive only; a saved spatial arrangement requires the archive **and** its matching sidecar. For dual-mode use, transport both and select the desired command. Copying the archive alone remains valid and produces a fresh conservative spatial import, not recovery of a missing authored layout. Single-file transport of authored spatial metadata is a possible later extension, not a v0.3 claim.

- `GET /api/project`: return safe manifest summary (PDF path, digest, page count, *validated* media placements); no OS paths or arbitrary source file contents.
- `GET /api/spatial`: return sidecar if validated; otherwise report no layout or a specific hash/schema mismatch.
- `PUT /api/spatial`: write **only** the CLI-chosen sidecar path. Do not accept a destination path from the browser; require JSON schema validation in Python, matching PDF hash, appropriate size limits and edit revision/ETag conflict detection.
- Protect writes using an unguessable per-process token and same-origin/Origin checks; token is accessible only to the launched local UI. A local server is *not automatically trusted* just because it is bound to loopback. Reject cross-site requests and unknown content types.
- Save atomically via temporary file in the destination directory + replace; retain original on validation/write failure. On stale sidecar, show explicit re-import/repair action; **never silently overwrite** user edits.
- The app is offline, not multi-user. No local database, cloud sync, general file uploads, or arbitrary URL fetches in this prototype.
- If the directory is read-only, allow exploring and presenting, but display clear read-only status rather than claiming to have saved.

### Packaging and distribution

- Keep new TypeScript dependencies in `frontend/spatial/`, not in core Python runtime unless actually needed.
- Include compiled frontend assets, matching PDF.js worker, and the CMaps, standard fonts, ICC profiles, WASM decoders, and other resources required by the supported PDF corpus in the built wheel. Resolve these locally. Test **`pip install <built wheel>`** without Node; development may use npm/pnpm. Keep a frontend lockfile, dependency/license inventory, and documented reproducible build. Verify the source distribution either includes the required built assets or has an explicit build-tool requirement; it must not silently download frontend code at runtime.
- Verify `pack`, `inspect`, and `present` without a browser, Node, or frontend initialization, including malformed/stale adjacent spatial sidecars. Verify spatial launch with pdfpc absent. A selected route may report its own missing runtime requirement; it must not break the other route.
- Do not load fonts, JS, CSS, PDFs, videos, or workers from the Internet. Validate with network disabled.
- No `.beamerpkg` schema v2 until the editor/viewer works and a migration plan for v1 archives is written.

## 9. Implementation gates: evidence, exit criteria, and stop rules

### Development branch and stopping procedure

Do all spatial planning and implementation on `feat/spatial-prototype`, created
from the verified `main` baseline before starting Gate 0. The baseline observed
on 2026-11-01 is `2e86c6f3be328f6c55d42ac0d792084d1372e95d`
(package 1.2.0). If `main` has advanced before setup, inspect that change and
record the actual branch point; do not reset it to this historical observation.

- Create and check out the feature branch, then commit this plan there before
  implementation. Branch creation alone does not isolate uncommitted files.
- Keep the scoped contributor-guidance changes, frontend experiments, tests,
  and gate reports on this branch. Commit each reviewed slice so its state can
  be retained without carrying tracked edits when switching branches.
- Keep `main` usable as the existing pdfpc package. Do not merge spatial work
  into it, publish the branch, or release the prototype without a separate
  instruction. Passing a gate does not authorize integration or publication.
- At a failed gate or a decision to stop, retain the feature-branch commits
  and failure evidence. Commit only owned work there before switching back to
  `main`; preserve unrelated edits and untracked files. Do not reset, revert,
  clean, or delete the experiment to recover the existing package.
- Resume by returning to the retained feature branch and its recorded gate.
  Abandoning spatial development leaves `main` unchanged and requires no
  repository rollback.

Use the installed guarded Git workflow. If it cannot create branches, the user
creates the branch before the agent commits or starts implementation; do not
bypass the guard. No branch creation is asserted by this planning document.

### Gate 0 — Feasibility and contracts (must precede UI commitment)

**Tasks**

1. After implementation is separately authorized, first append the concrete optional-spatial requirement to `docs/MVP.md`, create `docs/SPATIAL_MVP.md`, and add narrow `AGENTS.md` / `REVIEWING.md` addenda. Preserve the existing route, exclusions outside spatial work, and historical evidence. Complete this before UI prototypes or new spatial behavior.
2. Freeze route-isolation, navigation/media identity, restore, rendering-scope, and numeric archive/render resource contracts. Add bounded spatial archive admission before existing validation reads; preserve existing command behavior.
3. Build demo PDFs with existing `examples/build_demo.sh` without changing the LaTeX. Record PDF hashes, tool versions, and actual `/Movie` and pdfpc `/Launch` geometry/options in `docs/spatial/GATE0_REPORT.md`.
4. Prototype one ordinary and one cropped/rotated PDF page with PDF.js. Compare text/vector/math rendering against a trusted PDF viewer; document tolerances, poster behavior, and unsupported PDF features.
5. Benchmark **React Flow vs simple DOM viewport** with the same 30–50-page workload, one three-overlay frame group, a region-focus action, drag/zoom, and the two demo media forms. Quantify startup, responsiveness, CPU/memory trend, cache eviction, animation interruption, and element continuity on target hardware. No full editor.
6. Pin frontend versions/licenses and verify PDF.js point conversion and React Flow camera/keybinding APIs against installed versions. Demonstrate local loading of all necessary worker/font/decoder resources; browser policy/security overrides cannot establish acceptance.
7. Choose the canvas adapter in `docs/spatial/ADR-001-canvas-engine.md` using the shared workload and documented tradeoffs. Treat both candidates fairly; do not build a general whiteboard abstraction.

**Exit:** Scope documentation precedes prototypes; route and resource contracts are explicit; real media inventory and coordinate evidence exist; library choice is justified; renderer limitations and locally required resources are documented. **Stop** if demo media rectangles cannot be recovered reliably, or PDF.js corrupts essential scientific content without a plausible fix. No full editor yet.

### Gate 1 — Minimal read-only guided spatial viewer

**Tasks**

1. Define/version the five-part model (`FrameSource`, `CanvasObject`, `Viewpoint`, `PathStep`, runtime `NavigationSnapshot`) and validation.
2. Implement explicit grouping from hand-authored metadata, with frame overlay state changes at fixed canvas placement; no automatic grouping heuristics.
3. Render PDF via PDF.js; generate a conservative one-page-per-frame default grid when no sidecar exists.
4. Implement semantic object/world bounding-box camera target, short cancelable transitions, reduced-motion option, guided forward/back, exploration/overview and exact restore.
5. Test page-subregion zoom, normalized coordinates, resize and high-resolution rerendering.

**Exit:** Can present a scientific fixture with overlays in place, show detail, detour, and resume without unintended jumps. Video may be an unplayed poster at this gate; **Gate 1 alone is not an accepted v0.3 release.**

### Gate 2 — Both supported video forms in spatial mode

**Tasks**

1. Add `MediaPlacement` per-annotation API while preserving legacy discovery behavior.
2. Map placement rectangles onto the correct PDF page/overlay with viewport conversion.
3. Implement central media lifecycle and stable video layer; both click-to-play and pdfpc-style autostart/loop.
4. Handle browser autoplay rejection visibly; enforce active-instance exit/hidden-tab pause, same-instance continuity, paused history restore, and HTTP Range support.
5. Run V01–V12 on real compiled demos, plus synthetic hostile/rotated annotations.

**Exit:** Both shipped demo video cases work under the defined browser policies, including pan/zoom and restore, with no ghost audio. The shared fixture still demonstrates unchanged pdfpc behavior. This is project-level compatibility coverage; each user talk only qualifies the route and media features it uses. **Stop** on geometry drift or uncontrolled media lifecycle.

### Gate 3 — Minimal editor + reliable local saving

**Tasks**

1. Drag/reorder canvas objects; manually group consecutive pages into frames with preview and undo.
2. Create and adjust semantic viewpoints for whole objects, regions, and overview/world rectangles; arrange named paths and overlay policies.
3. Implement `GET/PUT` local sidecar API, schema/hash/revision validation, atomic saves, stale hash warning and read-only error mode.
4. Add edit/present mode switch, basic accessible controls, and no editable controls in projected present mode.
5. Verify fully offline built-wheel install, no Node requirement for end users, and safe local HTTP boundary.

**Exit:** A freshly built package can be imported, arranged, saved/reloaded without loss, and presented offline. Existing v1 archives remain unchanged.

### Gate 4 — Representative scientific talk / go–no-go

**Tasks**

1. Import a representative 20–50 physical-page scientific PDF with overlays, dense equations/TikZ, EBSD/microscopy images, and at least one video or supplementary clip.
2. Arrange a meaningful overview → subtopic → detail → experiment → result path; test non-linear audience questions.
3. Evaluate readability, audience orientation, recovery from wrong turns, time to a detail, and media controls. A dual-mode fixture may compare pdfpc and spatial where useful. A spatial-only evaluation does not require authoring or rehearsing a separate linear version of that talk.
4. Record blockers for the intended spatial use, including notes, timer, next-preview, two-display mode, remotes, browser/OS compatibility, and memory where relevant. Prioritize by user need; do not make pdfpc feature parity or replacement the success criterion.
5. Publish an evidence-backed `docs/spatial/PROTOTYPE_EVALUATION.md`; decide proceed/revise/stop. Do not treat an attractive animation demo as proof of value.

**Exit:** An evidence-backed proceed/revise/stop decision for the spatial route and a list of use-specific next requirements. Existing pdfpc support continues regardless of that decision. No requirement to convert existing talks, prepare both modes, achieve presenter parity, or introduce package schema v2.

## 10. Test strategy (Codex should implement before/with behavior)

| Test family | Must cover |
|---|---|
| Python unit: `pdf_media` | `/Movie`, recognized `/Launch`, duplicates, per-page/per-annotation identity, missing/rotated/cropped/nonfinite `/Rect`, blocked paths/options, preserve old discovery API. |
| Python unit: package/CLI | Existing `pack`/`inspect`/`present`, hash/media paths, separate `spatial`, cleanup, missing package/args; explicit route choice; no frontend initialization in existing commands; absent/malformed/stale sidecars do not affect them; spatial without pdfpc; pre-validation archive bounds. |
| Python server | Only allowlisted files, traversal/symlink/host/origin denial, token-protected writes, atomic save/ETag conflict, 200/206/416 ranges, request bounds, no source tree leakage. |
| TypeScript pure state | Overlay symmetry; per-object state and duplicate instances; guided anchor vs nested detour stack; resize-aware camera restore; interruption; same-instance video continuity; paused history restore; stable IDs and schema validation. |
| PDF geometry | PDF-space rect → viewport conversion including rotation/CropBox and zoom; preserved PDF aspect ratio; viewport resize; multiple annotation placements. |
| Browser (Playwright) | Real demo poster click; blocked autoplay fallback; stable media during transforms; instance exit/hidden-tab pause; seek and paused restore; duplicate-object independence; bounded cache/deep zoom; all offline resources; editor save/reload. |
| Scientific fidelity | Snapshot/reference comparison of equations, TikZ/vector, axes, alpha/transparent figures, high-resolution micrographs and overlay stability. |
| Regression | `poetry run pytest`, Ruff, mypy; frontend typecheck/build/tests; wheel install smoke; native pdfpc path and both media forms. |

**Test environment reporting:** Record OS, browser version, PDF.js/React Flow versions, hardware/display scale, GStreamer/pdfpc if used, and whether browser autoplay permissions were overridden. Never make a test pass by globally disabling browser security or silently muting audio.

### Route-choice acceptance matrix

Use shared fixtures to test these conditions once at project level. Do not require every user talk to implement every row or prepare both routes.

| Condition | Expected behavior |
|---|---|
| Existing archive, no spatial sidecar | `inspect` and `present` work as before; no spatial preparation or browser needed. |
| Malformed or stale adjacent spatial sidecar | `inspect` and `present` ignore it; `spatial` reports the issue and preserves the sidecar. |
| Spatial archive/layout on a machine without pdfpc | Spatial launch and the supported browser features work; no native-presenter probe or launch. |
| One archive used for both routes | Explicit command selects the route; no archive mutation, automatic switching, or required synchronization of presentation order. |
| Spatial sidecar omitted during transport | Archive remains valid; spatial offers a new import and does not claim to recover the authored layout. |
| Browser/frontend unavailable | Existing route works; spatial reports its selected-route requirement. |
| No video or no spatial authoring wanted | Existing media-optional packing remains valid; neither route requires unused media or the other route's metadata. |

### Minimum acceptance walk-through (shared dual-mode fixture)

1. `./examples/build_demo.sh` succeeds; no helper macro required for stock movie fixture.
2. `beamerpkg spatial examples/demo.beamerpkg` opens an **offline** local viewer; original `.beamerpkg` is unmodified.
3. Frame group overlays advance/backward in place with fixed camera.
4. Whole-frame/detail viewpoints zoom/pan smoothly; Escape unwinds a detour and returns the saved step/overlay/view. Test nested detours, direct guided resume, window resize, and paused media restoration.
5. Click-to-play bundled video works inside its PDF poster region; pan/zoom does not restart it.
6. Autostart/loop example works if browser policy permits, otherwise displays a working Play fallback. Changing active instance or entering overview/editing stops sound; a detail viewpoint on the same active instance preserves playback.
7. Save a layout/path to `demo.spatial.json`, restart viewer, reload identically; stale hash and invalid schema are correctly rejected.
8. `beamerpkg present examples/demo.beamerpkg` still works exactly as before under pdfpc.
9. Built wheel runs without dev npm/Node or Internet access.
10. Technical limitations, resource budgets, offline asset inventory, and benchmark results appear in project docs.
11. Route-isolation checks pass: stale sidecar leaves pdfpc usable, spatial works without pdfpc, and explicit commands always choose the requested route. No requirement to prepare two versions of each talk.

## 11. Proposed source layout (not rigid)

```text
src/beamerpkg/
  cli.py                    # add spatial command, leave present unchanged
  package.py                # reuse v1 package implementation
  pdf_media.py              # preserve discovery API, add per-annotation API
  spatial_model.py          # typed sidecar validation and hash bindings
  spatial_server.py         # localhost HTTP + Range + safe sidecar write API
  spatial_export.py         # trusted PDF media inventory serialization
  static/spatial/           # built SPA + locally bundled PDF.js worker
frontend/spatial/
  src/model.ts              # runtime schema and object/viewpoint types
  src/navigation.ts         # pure navigation reducer/state machine
  src/canvas/               # chosen adapter and camera target logic
  src/pdf/                  # page rendering, geometry, render-cache policy
  src/media/                # central media controller + video overlay
  src/editor/               # groupings, viewpoints, path editing
  src/App.tsx
  tests/                    # state, geometry, UI/browser tests
examples/                   # current demos unchanged; add scientific fixture
  spatial/                  # optional sidecar examples based on real built PDFs
tests/
  test_spatial_media.py
  test_spatial_server.py
  test_spatial_model.py
docs/
  SPATIAL_MVP.md
  spatial/GATE0_REPORT.md
  spatial/ADR-001-canvas-engine.md
  spatial/PROTOTYPE_EVALUATION.md
```

Avoid introducing a state management framework, database, GPU/WebGL engine, media transcoder, general-purpose file manager, or drawing editor without measured need.

## 12. Known risks and mitigation

1. **False overlay detection:** never guess frame grouping from nearly identical page pixels; manual grouping is correct for MVP.
2. **Video options not recoverable:** record *unknown* separately from false; allow validated sidecar overrides. Gate 0 decides achievable semantics.
3. **Autoplay policy:** handle rejected Promise; provide a user-gesture Play control. PDF-side pdfpc autoplay behavior does not automatically transfer to a browser.
4. **Annotation geometry:** rotation and CropBox/viewport mapping; test real and generated PDFs. Use supported PDF.js point conversion APIs.
5. **React component remount:** media lifetime must outlast PDF render/cache changes; test navigation while playing.
6. **Canvas library friction:** if React Flow keyboard/virtualization/overhead impairs scientific viewing, prefer simple transformed DOM; record decision, avoid rewriting entire app.
7. **Stale TeX rebuild:** PDF SHA binding prevents layout silently applying to shifted page indices; repair is explicit.
8. **Local-server security:** loopback alone is insufficient for write authorization; Origin/token checks and allowlists required. Validated ZIP contents should not be exposed indiscriminately.
9. **Large scientific PDF memory:** adaptive resolution, clipping/cache limits, cancellation and benchmarks rather than high-DPI rendering for every page.
10. **Two-file spatial transport:** intentional for v0.3; copy archive plus matching sidecar to preserve authored spatial layouts. Existing pdfpc transport remains one file. A later optional package extension needs its own backward-compatibility design.
11. **Scope creep:** presenter timer/notes, full collaboration, vector object editing, arbitrary media, Miro-style whiteboard features are outside the first technical prototype.
12. **Outdated repo instructions:** add spatial-specific scope notes instead of contradicting `AGENTS.md` in code or rewriting the original packaging MVP history.

## 13. Explicit non-goals

- No new equation/TikZ/LaTeX renderer or automatic conversion of scientific slides to editable browser widgets.
- No infinite collaborative drawing/notes/chat/sync platform, cloud login or server backend.
- No 3D camera, spin/rotation theatrics, timeline animation editor or content animation engine.
- No PowerPoint/Keynote authoring import, general arbitrary launch-link execution, web streaming or transcoding.
- No automatic commitment to pdfpc notes/countdown/two-monitor parity. Add spatial presenter features when a concrete intended use requires them. pdfpc remains a supported choice permanently within this plan, including after spatial mode matures.
- No forced migration of talks, dual-mode authoring requirement, automatic presenter selection, or silent cross-route fallback.
- No `.beamerpkg` container migration or archive mutation in this prototype.

## 14. Codex execution checklist and reporting contract

Codex should work in **small reviewable slices** and not claim completion at a gate without evidence. For each gate:

1. State the hypothesis and commands/fixtures used.
2. Add a failing test reproducing the intended behavior or failure mode where feasible.
3. Implement the smallest scoped change, with Python type hints/docstrings and strict TypeScript types.
4. Run focused tests, full regression suite, static analysis and browser smoke where applicable; report counts/failures rather than generic "tests pass".
5. Update the relevant spatial design/ADR/limitations document and cite external reference materials/frameworks.
6. Report what changed by file, what is still unsupported, any open risk, and the next gate's go/no-go recommendation.
7. Preserve a simple rollback: original `beamerpkg present` unaffected, spatial UI opt-in only. Report existing-route regression status separately from spatial gate acceptance. Gate completion does not authorize the next gate; stop for review as specified. A stopped spatial experiment must leave pdfpc use intact.

**Stop/seek review immediately** for any need to: rewrite PDF bytes or LaTeX typesetting, change rendering or command behavior of the existing pdfpc route, make existing commands depend on spatial metadata/frontend initialization, require both routes for every talk, rewrite `.beamerpkg` schema, automatically rebase stale layouts, execute arbitrary PDF actions, or introduce a custom video/PDF renderer. PDF.js rendering in the separately scoped spatial route is the intended design, not itself a stop condition.

## 15. References / acknowledgement for implementation

Internal source of truth:

- [beamerpkg README](https://github.com/ukerzel/beamerpkg/blob/main/README.md)
- [package.py](https://github.com/ukerzel/beamerpkg/blob/main/src/beamerpkg/package.py)
- [pdf_media.py](https://github.com/ukerzel/beamerpkg/blob/main/src/beamerpkg/pdf_media.py)
- [cli.py](https://github.com/ukerzel/beamerpkg/blob/main/src/beamerpkg/cli.py)
- [demo.tex](https://github.com/ukerzel/beamerpkg/blob/main/examples/demo.tex)
- [AGENTS.md](https://github.com/ukerzel/beamerpkg/blob/main/AGENTS.md) / [REVIEWING.md](https://github.com/ukerzel/beamerpkg/blob/main/REVIEWING.md)

External technical references (credit/document their contribution in the repository):

- [React Flow API: ReactFlowInstance](https://reactflow.dev/api-reference/types/react-flow-instance), [canvas interactions](https://reactflow.dev/api-reference/react-flow) and [utility classes](https://reactflow.dev/learn/customization/utility-classes).
- [PDF.js examples and viewport transformation](https://mozilla.github.io/pdf.js/examples/); [June 2026 removal of `convertToViewportRectangle`](https://bugzilla.mozilla.org/show_bug.cgi?id=2047366); [PDF.js document loading options and local resources](https://mozilla.github.io/pdf.js/api/draft/module-pdfjsLib.html). These were checked during the feasibility review; confirm exact behavior against the pinned installed version.
- [MDN: autoplay and media policy](https://developer.mozilla.org/en-US/docs/Web/Media/Guides/Autoplay); [HTMLMediaElement.play() failure modes](https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement/play).

---

**Definition of complete v0.3 prototype:** Spatial mode can import the current Beamer demo, organize logical frame groups, present guided or exploratory viewpoints with overlays in place, play both supported packaged video forms under explicit browser policies, and securely save/reload its adjacent sidecar offline within documented resource budgets. The existing pdfpc route remains usable independently, including without spatial metadata or frontend initialization; spatial mode runs without pdfpc. A representative scientific talk evaluates the value of spatial navigation. Authors may choose either route or both for each talk, with no replacement, migration, dual-authoring, or presenter-parity requirement.
