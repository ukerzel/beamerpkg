# The spatial route

beamerpkg provides two first-class routes: pdfpc, usually the main one, and the
spatial canvas. Neither requires the other. This guide covers the spatial one
and its support limits. The spatial route is included in version 1.3.0,
following its merge into `main` on 2026-11-03. Version 1.2.0 had the pdfpc route only.

Install the released package with `python -m pip install beamerpkg`. Its wheel
includes the browser app and local resources; the setup below is for development.

## Choose the route per talk

```bash
beamerpkg present talk.beamerpkg       # pdfpc route
beamerpkg spatial talk.beamerpkg       # spatial route
```

Use either command, or both with one archive. The spatial route needs a
supported browser but no pdfpc. The pdfpc route needs no browser, spatial
layout or frontend tooling.

## Set up a checkout

From the repository root, install the Python environment and build the local
browser app:

```bash
poetry install
(cd frontend/spatial && npm ci && npm run build)
```

Python 3.11+ and Poetry are required. Node 22.13+ and npm are build tools; a
built wheel includes the app, PDF.js worker and resources. End users need a
browser, but no Node/npm or pdfpc for this route. The tested browser is Chromium
on Linux; broader browser/OS support has not been qualified.

The demo and teaching fixture also need a working TeX environment with the
packages listed in [README](../../README.md#install-for-development). Their
video/poster assets are committed; no video generation or transcoding is needed.

## Try the demo talk spatially

After setup, the showcase is the same `examples/demo.beamerpkg` used for pdfpc:

```bash
./examples/build_demo.sh                           # PDF, archive, and layout
poetry run beamerpkg present examples/demo.beamerpkg   # pdfpc, two screens
poetry run beamerpkg spatial examples/demo.beamerpkg   # spatial canvas
```

`build_demo.sh` runs `tools/demo_spatial_layout.py`, which writes
`examples/demo.spatial.json` bound to that build's PDF hash. Recompilation can
change the PDF bytes, so the layout is generated after each build. If you
edit `demo.tex` so that its page mapping changes, update `FRAMES` and the expected
`PAGES` in that tool. The script regenerates example PDFs/packages, including
`examples/wrapperless.pdf`; use the isolated fixtures below to preserve them.

The canvas puts the title at the centre with the talk's four acts around it
clockwise: the problem (left), Beamer stays Beamer (top), media (right) and
shipping (bottom). The default `tour` path zooms into the Lagrangian, then
into the Higgs potential, where the next steps drop the ball into the vacuum
in place. It then zooms into the click-to-play video and ends on the whole
canvas. The pdfpc-specific frames (page transitions, presenter screen) are
small satellites off the tour. The `deck` path in the dock's path menu plays
every frame in its original order, backup included.

Backup material follows the talk after `\appendix`: three parts (A physics,
B container, C spatial internals), each a dark divider with the part letter
plus three frames. On the canvas they form a band below the talk, one tight
2×2 cluster per part. Frames within a part almost touch, while parts sit far
apart from each other and from the talk. The tour never enters them but its
finale shows them, and a click flies into any backup frame. From there → and
← step through the backup (the dock's path menu shows `backup`); Esc or
"Back to tour" returns to where you left the tour. In general, arrows on a
frame that the current path does not visit follow the shortest path that does.
A frame on the current path stays a plain detour, where → resumes. For questions, open
**Views** and pick `backup-physics`, `backup-container` or `backup-canvas` (the
drawer shows each cluster as a miniature), or switch to the `backup` path. In
pdfpc the backup frames come after "Try it": the frame counter and progress bar
cover the talk only, and the footline labels the frames A.1, A.2, …

## Build and try the teaching fixture

After setup, from the repository root:

```bash
poetry run python tools/build_spatial_fixtures.py
poetry run beamerpkg spatial build/spatial-fixtures/science.beamerpkg
```

The fixture builder compiles into `build/spatial-fixtures/authoring` and does
not overwrite existing example PDFs. It also creates demo, wrapperless and
40-page repeated-content stress packages for developer checks.

The server prints a `http://127.0.0.1:PORT/` URL and opens a browser. If browser
opening is unavailable, open the displayed URL manually. For headless testing,
use `--no-browser`. Keep the foreground command running; Ctrl+C stops it and
removes extracted files. Only the local loopback endpoint is served.

## Present and explore

- Right / Down / Space / PgDn advances an overlay, then the next path step.
  Left / Up / PgUp reverses overlays and steps (presentation clickers usually send
  PgUp/PgDn). A fixed-overlay detail step is one path step.
- Overview or O shows the whole canvas with the guided route and numbered
  stops; clicking a number jumps to that step (discarding detours), clicking a
  frame flies into it as a detour. The same applies on a guided whole-canvas
  step, such as the demo's finale, which also offers Start over. Views (V) opens previews of every
  whole-frame/detail target for a temporary detour. Double-click a frame to
  focus it. M toggles the minimap, F fullscreen, ? or H the shortcut sheet.
- Camera moves zoom out, travel and zoom back in (smooth zoom/pan path). While
  presenting, the control dock, status and cursor hide after a few idle
  seconds; moving the mouse brings them back. Non-active frames are dimmed.
- Drag to pan; wheel to zoom. Exploring keeps the guided resume point.
- Esc or the Return button unwinds one detour; Enter is not a return shortcut.
  In exploration, a presentation arrow returns to the guided resume point
  without advancing, unless the focused frame is off the current path: arrows
  then follow the shortest other path containing it, with Esc returning home.
- Play starts video in its PDF rectangle. Camera/detail changes on the same
  active instance retain playback. Overview, leaving that instance, or hiding
  the browser tab pauses it. Returning from history restores its position
  paused. An autostart request may be blocked; use the visible Play control.
- Browser/system reduced-motion preference makes camera transitions instant.

Overlay changes retain the previous sharp render until the new page is ready,
then crossfade. This is viewer behavior; PDF page-transition effects are not
replayed. Deep zoom rerenders visible PDF content rather than stretching the
overview thumbnail. Raster images retain the detail already embedded in the PDF.

The path menu selects a path and restarts at its first step, discarding detours.
The first path in a layout is selected at launch. There are at most 32 nested
detours; reaching that limit leaves the saved resume point intact and shows a
notice. Keyboard navigation is left to focused input/select/video controls;
Space on a focused button activates that button.

The scientific fixture is synthetic teaching material, not a validated
scattering calculation or a claim about EBSD indexing. It demonstrates three
overlays, equations and translucent bands, a nearby result, detail views,
supplementary detours and both existing packaged-video forms.

## Prepare another talk

Compile and pack as usual:

```bash
poetry run beamerpkg pack talk.pdf --root .
poetry run beamerpkg spatial talk.beamerpkg
```

Without a sidecar, every physical PDF page becomes a separate frame in a grid.
Overlay grouping is explicit; visually similar pages are never guessed.

For an authored layout, prepare `talk.spatial.json` beside the archive, using
the current schema below. The fixture builder writes a working example at
`build/spatial-fixtures/science.spatial.json`. The broader
[spatial plan](../SPATIAL_PLAN.md) also describes future editor/save features;
it is a design record rather than the current user interface.

Layouts are read-only at runtime. There is no graphical editor or Save button.
An invalid/stale sidecar is rejected without modification; rebuilding a PDF
requires manual layout review and rebinding. The pdfpc route ignores that
sidecar and remains usable. No presenter is selected or launched automatically
because a sidecar happens to exist.

To transport an authored spatial presentation, copy the archive **and** its
matching adjacent sidecar. pdfpc still needs only the archive. Copying only the
archive does not retain authored spatial placement/path metadata.

## Current sidecar schema

Read the presentation path and SHA-256 from
`poetry run beamerpkg inspect talk.beamerpkg --json`. The `source` object below
must use those exact values from `presentation.path` and `presentation.sha256`.
Replace the example hash before use. This layout presents the first PDF page,
then a detail of it, then a whole-canvas view:

```json
{
  "format": "beamerpkg-spatial",
  "schema_version": 1,
  "source": {"pdf_path": "talk.pdf", "pdf_sha256": "REPLACE_WITH_PRESENTATION_SHA256"},
  "frames": [{"id": "f0", "page_indices": [0]}],
  "objects": [{"id": "o0", "frame_id": "f0", "x": 0, "y": 0, "width": 960}],
  "viewpoints": [
    {"id": "whole", "target": {"kind": "object", "object_id": "o0", "region": [0, 0, 1, 1]}},
    {"id": "detail", "target": {"kind": "object", "object_id": "o0", "region": [0.2, 0.2, 0.4, 0.4]}, "padding": 0.03},
    {"id": "canvas", "target": {"kind": "world_rect", "rect": [-100, -100, 1160, 800]}}
  ],
  "paths": [{"id": "main", "steps": [
    {"id": "s0", "viewpoint_id": "whole", "overlay_policy": "all"},
    {"id": "s1", "viewpoint_id": "detail", "overlay_policy": "fixed", "overlay_index": 0},
    {"id": "s2", "viewpoint_id": "canvas", "overlay_policy": "fixed"}
  ]}],
  "media_overrides": []
}
```

- Frames group zero-based, consecutive, nonoverlapping page indices. Grouped
  pages must have the same visible geometry and rotation. For three overlays,
  use `[0, 1, 2]`; remove those pages from any other frame groups.
- Objects place frames in world coordinates; height follows the frame's aspect
  ratio. More than one object may refer to a frame, with independent runtime
  overlay and playback positions.
- Object `region` and world `rect` both use `[x, y, width, height]`. Object
  regions are normalized to the displayed page, with a top-left origin and
  must stay inside `[0, 1]`. World rectangles use canvas units. Width/height
  must be positive. `padding` is optional, from 0 to 0.45 (default: 0.06).
- An `all` step visits each overlay, starting at the first on forward entry
  and the last on backward entry. It cannot set `overlay_index`. A `fixed`
  step selects a zero-based overlay (default: 0). World targets require
  `fixed` and have no `overlay_index`.
- IDs start with an ASCII letter or digit, then use ASCII letters, digits,
  `_`, `.` or `-`, up to 64 characters. IDs must be unique in each collection;
  step IDs must be unique within their path. All references must resolve. Unknown fields,
  duplicate JSON keys, invalid numbers and stale PDF bindings are rejected.
- `media_overrides` must be an empty list. No media override or authoring
  history is persisted by the viewer.

If a PDF is rebuilt, retain the old layout separately, check its page mapping,
then update its binding or prepare a new layout explicitly. There is no automatic
rebase or re-import command. A hand-authored layout may select a subset of pages
and may order them independently of the PDF's linear order.

## Media and support limits

The supported annotation forms and options are listed in
[README](../../README.md#standard-beamer-no-beamerpkg-latex-helper-required).
The spatial route reads placement identity and rectangles from the unchanged
PDF and checks paths against the validated asset inventory. It does not execute
PDF actions. Ordinary PDF links, `/Trans` transitions, embedded notes and
embedded media are not implemented as spatial features.

Native video controls appear when `/ShowControls` is explicitly true; false
and absent flags are not treated as true. The viewer also provides a Play/Pause
control. Only one placement is active at a time. If a page has several autostart
placements, select one explicitly. Browser autoplay rejection gives a manual
Play fallback; unsupported codecs or malformed video produce a visible error.
Unknown flags stay unknown, and unsupported encoded playback options are
rejected rather than approximated. Crop/rotation placement is tested, but
rotated video-content orientation has not been qualified.

The size, count and compression limits below apply to spatial launch; `pack`,
`inspect` and `present` do not impose them. Archive path/hash validation applies
to both routes.

| Resource | Limit |
|---|---|
| Archive | 512 MiB; at most 4,096 ZIP entries; no duplicate/noncanonical paths or symlinks |
| Expanded files | 256 MiB per entry, 1 GiB total, compression ratio at most 200 |
| Manifest / adjacent layout | 1 MiB / 512 KiB |
| PDF pages / placements | 200 / 2,000 |
| Frames / objects / viewpoints / paths | 200 / 400 / 800 / 32 |
| Path steps | 2,000 total across all paths |
| World coordinates / object width | Absolute x/y at most 1,000,000; width positive and at most 100,000 |
| Canvas buffers | Below 128 MiB of RGBA; one PDF render at a time; dimensions at most 8,192 |

Thumbnails share an 18.5-million-pixel budget, at most one million pixels each.
Detail, replacement and crossfade buffers are at most four million pixels each;
at most 48 viewpoint previews add about one million pixels. The detail render
clips to the visible page region at deep zoom. This bounds canvas storage,
not total browser/worker/GPU or video-decoder memory.

The server accepts read-only requests at its printed loopback address. It serves
the bundled app, validated PDF, project data and referenced media only; notes
and editable sources are not browser endpoints. Audio/video formats depend
on the browser and system codecs. No CDN, transcoder or custom decoder is used.

## Build and check an installed distribution

After the frontend build and fixture build above:

```bash
poetry build --output build/spatial-dist
PLAYWRIGHT_BROWSERS_PATH=/tmp/beamerpkg-browsers poetry run python tools/check_spatial_distribution.py
```

The check needs a locally cached pypdf wheel and the development Playwright
browser; see [frontend setup](../../frontend/spatial/README.md). It installs
the experimental wheel in a fresh environment without index access, removes
Node/npm/pdfpc from that environment's PATH, relocates the archive/layout, and
drives the installed server using an external test browser. Non-loopback
browser requests are blocked. This is not OS network isolation.

Local validation builds stay under `build/spatial-dist`. Final 1.3.0 release
artifacts are retained separately in `dist/`; publish only the exact wheel and
sdist validated for the release, rather than unrelated files in that directory.

## Human walkthrough before relying on it for a talk

1. Present the workflow, advance the scattering frame through all three
   overlays in place, and reverse them.
2. Open a detail and a supplementary result. Return to the exact planned
   overlay and check whether that is understandable while speaking.
3. Play each video form, zoom/pan, seek, leave, and return. Confirm sound stops
   when expected on the actual browser/audio/display setup.
4. Rehearse your own research PDF's equations, images, colors and required
   magnification. Compare its appearance with your normal PDF viewer.
5. Decide whether this route helps this talk. Continue using pdfpc for talks
   that need its notes, timer, next preview or dual-screen presentation.

Automated checks establish the implemented software behavior on the tested
Linux/Chromium setup. They do not establish audience comprehension, broad
browser/OS support, all scientific PDF fidelity, or live pdfpc parity.

## Generated files and branch switches

The spatial route is part of `main`. Its compiled assets under
`src/beamerpkg/static/spatial` are ignored/rebuildable and are not isolated by
Git branch switches. Rebuild from the current frontend lockfile before making
a wheel or sdist. Preserve generated outputs separately before checking out a
historical branch whose build must not pick them up. The fixture builder under
`build/` is the way to check fresh PDFs without replacing example outputs.
