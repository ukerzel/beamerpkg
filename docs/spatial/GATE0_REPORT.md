# S2 / Gate 0 feasibility report

Date: 2026-11-01. Baseline: S1 `20bd4de`; S2 working-tree producers and
dependency lockfile are retained in the same commit as this report.
Decision: **proceed with the DOM viewport** to the read-only viewer rung S3.

## Fixtures, environment and commands

Ubuntu 26.04.1 under WSL2, Linux 6.18.54.1; Playwright Chromium
156.0.8078.4, viewport 1280×800, DPR 1. Pinned versions: PDF.js 6.4.299,
React/React DOM 19.3.1, React Flow 12.12.0 (probe only), Zod 4.6.7,
TypeScript 7.0.2, Vite 8.3.5, Playwright 1.64.1. Exact transitive identities
are in `frontend/spatial/package-lock.json`.

```bash
poetry run python tools/build_spatial_fixtures.py
cd frontend/spatial
npm ci
node scripts/resources.mjs --dev
PLAYWRIGHT_BROWSERS_PATH=/tmp/beamerpkg-browsers npx playwright install chromium
npm run typecheck
PLAYWRIGHT_BROWSERS_PATH=/tmp/beamerpkg-browsers npm test -- --grep 'real PDF'
```

The builder compiles the unchanged demo/wrapperless sources twice in an
isolated authoring directory without touching existing example outputs, then
packages them. It also builds the synthetic science teaching fixture (8 pages,
3 in-place overlays, equations/vector/transparency and both videos) and a
40-page repeated-content stress PDF. Stress duplicates real demo pages and
does not represent an independent research deck. Real page counts, PDF hashes,
rectangles, and decoded flags are retained in
[inventory.json](evidence/s2-20261101/inventory.json).

## Observation

Two complete two-adapter browser runs passed (2 tests each); the second run's
metrics are retained below. The same repeated-content PDF, 320px thumbnails,
layout and MP4 were used. Both mounted 40 surfaces, with no remount on ten
camera updates while actual MP4 currentTime advanced. Both fetched only local
resources. No autoplay-policy/security overrides or muting were added.

| Diagnostic | DOM | React Flow |
|---|---:|---:|
| PDF + 40 thumbnail load, ms | 3830.8 | 3340.2 |
| Ten camera-command round trips, ms | 90.3 | 101.7 |
| CDP main-thread TaskDuration delta, seconds | 2.752 | 2.402 |
| CDP JavaScript heap sample, MiB | 52.0 | 57.7 |
| Estimated equivalent thumbnail RGBA, MiB | 8.79 | 8.79 |
| Additional surface mounts during movement | 0 | 0 |

These are individual developer observations, not a speed ranking or FPS claim.
Contexts were fresh but OS/Vite caches were shared/uncontrolled. Worker/GPU/
decoder allocations are not included in JS heap or thumbnail estimates. The
probe uses blob thumbnails; production cache enforcement/cancellation is S3.
CPU diagnostics use Chromium's
[Performance domain](https://chromedevtools.github.io/devtools-protocol/tot/Performance/),
not whole-system CPU accounting.

A later overlay-swap run hit the default five-second DOM readiness assertion;
the [failure and correction](evidence/s2-20261101/readiness-failure.md) are
retained. Startup is diagnostic under this contract; use a bounded 45-second
readiness wait and continue reporting actual timing. Do not read the earlier
successful samples as a guarantee that all startup times are below five seconds.
With the corrected wait, both adapters passed again, including repeated
source-page swaps within one existing surface while the video remained stable.

## Geometry and appearance

- The compiled standard movie's `/A` retains `/Mode /Repeat` and controls;
  pdfpc's `/Launch /F` retains `?autostart&loop`. Neither action is executed.
- PDF.js warns that Movie annotations are unimplemented. It still renders the
  underlying Beamer poster as PDF page content. The HTML video must supply
  playback; importing the PDF alone is insufficient.
- A deliberately cropped page with CropBox `[20,15,420,240]`, rotated 90°,
  maps rectangle `[100,60,300,180]` to normalized
  `[0.2,0.2,0.5333333333,0.5]`. Both tests match these independently specified
  values; the viewport corner calculation has zero error at scale 1.
- PDF.js `convertToViewportPoint` is available and
  `convertToViewportRectangle` is absent in the installed API. Version 6
  document teardown is `pdf.loadingTask.destroy()`, not `pdf.destroy()`.
- The agent inspected [PDF.js science rendering](evidence/s2-20261101/science.png)
  against the [Poppler reference](evidence/s2-20261101/science-poppler.png):
  equation symbols/layout, axes/grid, colored bands, and translucent overlaps
  remain readable. Antialiasing differs, including fine equation bars; no pixel
  identity is claimed. [Rotated/cropped output](evidence/s2-20261101/rotated.png)
  intentionally clips the title at the selected CropBox boundary.

Raw diagnostics: [DOM](evidence/s2-20261101/dom.json),
[React Flow](evidence/s2-20261101/flow.json),
[environment](evidence/s2-20261101/environment.json).

## Limits and remaining gates

No essential rendering/geometry blocker appeared in these fixtures. Full
guided navigation, deep-zoom bounded rerendering, autoplay/error/hidden-tab
policy, range seek, production server security, installed-wheel offline proof,
and a human presentation walkthrough are not established by this probe.
Continue with S3; do not claim lecture or audience acceptance.

Runtime packages use Apache-2.0 (PDF.js) and MIT (React/React DOM/Zod and
their MIT scheduler). The resource build copies dependency license texts and
local CMaps/fonts/ICC/WASM; no CDN will be used. React Flow remains a pinned
MIT developer-only comparison, not a second production engine. Browser binaries,
node_modules, generated bundles, and fixture packages are not part of this S2
source/evidence commit.
