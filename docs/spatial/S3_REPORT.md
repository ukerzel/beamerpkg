# S3 — read-only spatial viewer

Date: 2026-11-01. S2 baseline: `1b41ff0`.
Decision: proceed to installed-distribution proof S4 after commit/push.

The opt-in `beamerpkg spatial ARCHIVE [--no-browser]` now starts a foreground,
ephemeral loopback server. It reads the adjacent validated sidecar or generates
a conservative layout, serves only the bundled app/PDF/runtime media, and
removes temporary extraction after Ctrl+C. There is no editor or writable API.

The DOM viewer provides path controls, in-place grouped overlays, whole-frame
and region views, overview, pointer exploration and nested return. Media
elements survive same-instance viewpoint changes independently of PDF
resolution changes. Rendering uses one queued PDF.js task, bounded thumbnails,
and clipped detail buffers; these are canvas bounds, not a claim about total
browser/worker/GPU RAM.

## Validation

```bash
poetry run pytest -q
poetry run ruff check .
poetry run mypy src
poetry check --lock
cd frontend/spatial
npm run build
PLAYWRIGHT_BROWSERS_PATH=/tmp/beamerpkg-browsers npm test
```

- 57 Python tests passed: includes existing regressions, spatial admission/model,
  HTTP host/origin/path denial, byte ranges/HEAD, read-only methods, cleanup,
  malformed PDF handling, visible CropBox/MediaBox intersection, and legacy
  commands running in a fresh process that rejects all spatial imports.
- Ruff passed; mypy passed for seven source files; Poetry lock check passed.
- Frontend strict typecheck and production build passed. Vite reports a large
  app chunk (~760 kB uncompressed including PDF.js); this is diagnostic and
  does not introduce online fetches or a second renderer.
- 18 frontend tests passed: nine runtime-model controls, three navigation
  state tests, two adapter probes and four production-bundle browser tests.
  The production tests use actual loopback serving, with non-local requests
  blocked. They cover overlay symmetry with fixed camera, details, nested
  restoration, resize, real click-to-play/seek, measured same-video detail zoom,
  stable video element, overview/page-exit pause, and real pdfpc-requested
  autoplay according to browser policy.
- A separate injected `NotAllowedError` proves the visible manual fallback
  still plays the real video. Injected hidden/visible document state proves
  the pause/resume policy. These controls are not observations of OS-level tab
  switching or universally permitted autoplay. No policy override/muting is used.

[Final sharp scientific view](evidence/s3-20261101/science-viewer.png) and
[visible canvas dimensions](evidence/s3-20261101/buffers.json) are retained.
The screenshot waits for the correct high-resolution overlay, rather than
capturing a stretched loading thumbnail. The agent inspected this output;
human lecture acceptance and installed-wheel behavior remain pending S4.

## Failures retained and corrected

- Initial TypeScript errors exposed untyped test element callbacks. A chained
  test invocation ran against the previous bundle after that build failed;
  its failures were retained under `build/spatial-evidence/s3-initial-stale-build`.
  Subsequent browser runs followed a successful build as a separate step.
- The stronger video-detail test exposed a real interruption bug: closing the
  Views sidebar resized the canvas, cancelled a focus animation and lost its
  target. Preserving the pending semantic/restore target through resize fixed
  it. The failed trace/context remains under
  `build/spatial-evidence/s3-resize-interruption-failure`.
- Native media play/pause/error events now update visible status, so browser
  controls cannot leave a false Playing indication. Restored paused media can
  display its retained frame.

## Boundaries

Existing `package.py` and package schema are unchanged. pdfpc subprocess tests
prove argument order/extraction, not a new live desktop playback observation.
The new route requires a supported browser, and the repository's compiled
frontend must be built before use; wheel/sdist inclusion is explicit. Compiled
assets, browser binaries, node_modules and generated archives are ignored in
Git and reproducible from the pinned source/tooling. S4 must still prove a
fresh installed wheel works without Node/pdfpc/checkout dependencies.
