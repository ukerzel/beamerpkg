# Try the first spatial MVP

This prototype lives on `feat/spatial-prototype`. The published 1.2.0 package
and `main` retain the existing pdfpc workflow. No release or merge has been made.

## Choose the route per talk

```bash
beamerpkg present talk.beamerpkg       # existing pdfpc route
beamerpkg spatial talk.beamerpkg       # optional spatial route
```

Use either command, or both with one archive. Spatial mode needs a supported
browser; pdfpc is not required for it. The existing route needs no browser,
spatial layout, or frontend tooling.

## Try the demo talk spatially

The showcase is the same `examples/demo.beamerpkg` used for pdfpc. One archive
serves both routes:

```bash
./examples/build_demo.sh                           # PDF, archive, and layout
poetry run beamerpkg present examples/demo.beamerpkg   # pdfpc, two screens
poetry run beamerpkg spatial examples/demo.beamerpkg   # spatial canvas
```

`build_demo.sh` runs `tools/demo_spatial_layout.py`, which writes
`examples/demo.spatial.json` bound to that build's PDF hash. pdflatex output
changes per build, so the layout is generated rather than committed. If you
edit `demo.tex` so that its page count changes, update `FRAMES` in that tool.

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
finale shows them, and a click flies into any backup frame. For questions, open
**Views** and pick `backup-physics`, `backup-container` or `backup-canvas` (the
drawer shows each cluster as a miniature), or switch to the `backup` path. In
pdfpc the backup frames come after "Try it": the frame counter and progress bar
cover the talk only, and the footline labels the frames A.1, A.2, …

## Build and try the teaching fixture

From this branch's repository root:

```bash
poetry install
cd frontend/spatial
npm ci
npm run build
cd ../..
poetry run python tools/build_spatial_fixtures.py
poetry run beamerpkg spatial build/spatial-fixtures/science.beamerpkg
```

Node/npm are development tools used to build the bundled app. A built Python
wheel includes the app, PDF.js worker and required local resources; its user
does not need Node/npm. These commands do not overwrite existing example PDFs.
The fixture builder requires the existing TeX environment and demo video.

The server prints a `http://127.0.0.1:PORT/` URL and opens a browser. If browser
opening is unavailable, open the displayed URL manually. For headless testing,
use `--no-browser`. Keep the foreground command running; Ctrl+C stops it and
removes extracted files. Only the local loopback endpoint is served.

## Present and explore

- Right / Space / PgDn advances an overlay, then the next path step. Left /
  PgUp reverses overlays and steps (presentation clickers usually send
  PgUp/PgDn). A fixed-overlay detail step is one path step.
- Overview or O shows the whole canvas with the guided route and numbered
  stops; clicking a number jumps to that step (discarding detours), clicking a
  frame flies into it as a detour. The same applies on a guided whole-canvas
  step, such as the demo's finale, which also offers Start over. Views (V) opens previews of every
  whole-frame/detail target for a temporary detour. Double-click a frame to
  focus it. M toggles the minimap, F fullscreen, ? the shortcut sheet.
- Camera moves zoom out, travel and zoom back in (smooth zoom/pan path). While
  presenting, the control dock, status and cursor hide after a few idle
  seconds; moving the mouse brings them back. Non-active frames are dimmed.
- Drag to pan; wheel to zoom. Exploring keeps the guided resume point.
- Escape / Return unwinds one detour. In exploration, a presentation arrow
  returns to the guided resume point without advancing; press again to advance.
- Play starts video in its PDF rectangle. Camera/detail changes on the same
  active instance retain playback. Overview, leaving that instance, or hiding
  the browser tab pauses it. Returning from history restores its position
  paused. An autostart request may be blocked; use the visible Play control.
- Browser/system reduced-motion preference makes camera transitions instant.

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

For an authored layout, prepare `talk.spatial.json` beside the archive. The
fixture builder writes a valid, hash-bound example at
`build/spatial-fixtures/science.spatial.json`. The schema and illustrative
object/frame/viewpoint/path structure are described in
[SPATIAL_PLAN.md](../SPATIAL_PLAN.md). Use descriptive IDs for your targets and
paths. `source.pdf_sha256` must be the manifest's presentation hash and
`source.pdf_path` its exact presentation path. Page indices are zero-based;
groups must be consecutive, nonoverlapping, and geometrically compatible.
This first MVP reserves `media_overrides` as an empty list.

Layouts are read-only at runtime. There is no graphical editor or Save button.
An invalid/stale sidecar is rejected without modification; rebuilding a PDF
requires an explicit layout re-import/repair. The pdfpc route ignores that
sidecar and remains usable. No presenter is selected or launched automatically
because a sidecar happens to exist.

To transport an authored spatial presentation, copy the archive **and** its
matching adjacent sidecar. pdfpc still needs only the archive. Copying only the
archive does not retain authored spatial placement/path metadata.

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

Experimental builds stay under `build/spatial-dist`; do not overwrite release
artifacts in `dist`. The prototype still uses package version 1.2.0 for local
testing. These files are not a new public release.

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

## Stop the experiment without rolling back main

Keep owned work committed on the feature branch. Before a later switch to a
main-only development/release build, preserve this branch's generated
`src/beamerpkg/static/spatial` directory under the ignored `build/` directory.
Generated files are not isolated by Git branches and could otherwise be picked
up by a main-only Python package build. Keep the pinned frontend sources and
retained evidence on the feature branch; rebuild its assets when resuming.
Do not reset/revert main, delete evidence, or clean unrelated files. The existing
pdfpc commands remain independent throughout.
