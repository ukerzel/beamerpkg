# First spatial MVP: technical evaluation

Historical S4 evaluation: the results and pending decisions below describe
2026-11-01. On 2026-11-03 the user completed a demo walkthrough and authorized
merging the route into `main`; subsequent fixes and current validation are in
[WORKLOG](../../WORKLOG.md). Use the [user guide](USER_GUIDE.md) for current
instructions. The dated evidence below is retained without changing its claims.

Date: 2026-11-01. Branch: `feat/spatial-prototype`.
Decision: the read-only first-MVP technical ladder S0–S4 is qualified on the
tested Linux/Chromium setup. Stop at the human walkthrough; do not start the
graphical editor, writable API, release, or merge automatically.

This implements the bounded [first-MVP contract](../SPATIAL_MVP.md), not the
entire broader v0.3 editor/save design. Existing pdfpc and optional spatial
presentation remain independent choices per talk.

## Result and evidence

| Check | Observed result | Scope |
|---|---|---|
| Python suite | 59 passed; Ruff, mypy for seven source files, Poetry lock check pass | Legacy regressions, admission/layout/media, read-only HTTP/Range, route isolation, cleanup |
| Frontend suite | 21 passed: 9 model, 3 navigation, 2 adapter probes, 7 production-viewer cases | Linux Chromium 156.0.8078.4; production-viewer cases at DPR 2 |
| TypeScript/build | Strict typecheck and production build pass | Locally bundled PDF.js 6.4.299, React 19.3.1, DOM viewport |
| Scientific fixture | 8 freshly compiled pages, 3 grouped overlays, vector equations/bands, detail/result/supplement, both video forms | Synthetic teaching fixture, not a scattering/EBSD validation |
| Stress fixture | Both adapters qualified on 40 repeated-content pages | Developer diagnostic; no general performance or audience claim |
| Distribution | Fresh wheel installed without index access; wheel/sdist include app, worker, CMaps/fonts/ICC/WASM, notices and TeX helper | Experimental artifacts under `build/spatial-dist`; not a release |
| Runtime independence | Installed module outside checkout; no Node, npm, or pdfpc on runtime PATH | The external developer test driver still uses Node/Playwright |
| Offline browser behavior | Non-loopback requests blocked; zero external attempts/page errors | Browser-request isolation, not OS network isolation |
| Real video | Packaged 10.005-second MP4 plays/seeks, returns 206 responses, retains element through detail zoom, pauses on overview/restore | Actual playback, no autoplay/security override or muting |
| Legacy route | Invalid spatial sidecar ignored by inspect/present; presenter arguments and extracted PDF remain correct | Fake presenter subprocess; no new live pdfpc rendering claim |
| Resource/camera controls | Deep zoom rerenders a clipped tile within pixel bounds; reduced motion and latest-target/resize interruption pass | Canvas accounting only, not total browser/worker/GPU RAM |
| Failure controls | Stale/malformed models, invalid decode bytes, blocked autoplay, hidden-tab policy, unsafe HTTP/assets | Injected controls labelled separately from native playback |

The final [distribution receipt](evidence/s4-20261101/distribution.json) records
the exact wheel/sdist sizes and SHA-256, installed Python module hash, source
base commit and working-tree source hashes, local dependency version, request
policy, actual video duration, range responses, archive preservation and
process-private temporary-file cleanup. Its code/content binding is stronger
than assuming that the base commit alone describes the final S4 working tree.

The [installed-wheel screenshot](evidence/s4-20261101/installed.png) shows the
scientific fixture rendered from that isolated installation. The agent inspected
the earlier science/Poppler references and sharp production output. A human
has not yet rehearsed this interface on the target presentation setup.

## Isolation and preservation

S0 plan/cold read was published as `2fa9f70`; S1 as `20bd4de`; S2 as
`1b41ff0`; S3 as `5450649`. A narrowly tested asset-boundary correction was
published as `af80080`: serve only referenced placement assets and force
non-media payloads to non-executable attachment/octet-stream handling. A
regression first returned 200 for unreferenced HTML, then passed after the fix.

`package.py`, archive schema v1, and `main` remain unchanged. Spatial imports
are lazy and absent from old commands. Notes/source payloads are not browser
surface. The source/media archive is not rewritten, and authored layouts remain
adjacent, exact-PDF-hash-bound, read-only JSON.

Compiled assets and caches are generated rather than committed. Before a later
main-only build, preserve this branch's generated static directory under the
ignored build tree as described in the [guide](USER_GUIDE.md); Git branches do
not isolate generated files. No rollback of main is required.

## Negative evidence and implementation corrections

- Gate 0's default five-second readiness timeout failed once; it was an
  unintended speed gate under a diagnostic-timing contract. The retained
  [failure](evidence/s2-20261101/readiness-failure.md) explains the bounded
  readiness wait and preserves actual startup measurements.
- The production viewer's stronger detail test exposed a real sidebar-resize
  interruption bug; pending targets now survive resize and obsolete animations
  cannot snap back. Trace/context is retained under
  `build/spatial-evidence/s3-resize-interruption-failure`.
- An initial browser invocation used a stale bundle after a typecheck failed.
  It is recorded in S3; later runs followed successful builds separately.
- The first distribution helper used an ambiguous glob and selected an old
  1.0.1 wheel. The first experimental build also reused the 1.2.0 release
  filenames in `dist`. Experimental output now has a separate directory and
  exact versioned selection. The published 1.2.0 artifacts were restored and
  verified against official PyPI hashes; the
  [restoration receipt](evidence/s4-20261101/released-artifacts-restored.json)
  records those bytes. No artifact was released/published.
- A later cleanup assertion counted unrelated concurrent test-server directories
  in shared `/tmp`. The installed proof now assigns its process a private
  temporary root. The false failure, screenshot and diagnosis remain under
  `build/spatial-evidence/s4-cleanup-assertion-failure`; the final proof checks
  only its own extraction/admission directories.

## Limits and next decision

The first MVP has no graphical editor, save API, notes/timer/next preview,
dual-monitor view, embedded media, arbitrary PDF action execution, transcoding,
or archive-contained spatial metadata. Manual JSON editing is required for
authored grouping and paths. Unknown playback flags remain unknown; encoded
options outside the supported demo forms and nonempty media overrides are
rejected visibly.

The current evidence does not establish every PDF feature, all scientific
color/typography cases, rotated-video content orientation, OS-level audio/tab
behavior, universal codecs/autoplay, broad browser support, arbitrary large
deck performance, or improved audience comprehension. Static cropped/rotated
page coordinates are independently checked; do not extend that to an untested
media-orientation claim. Geometry/resource limits and visible errors are part
of this prototype's support boundary.

Use the [human walkthrough](USER_GUIDE.md) with the teaching fixture and a real
research deck, then choose proceed/revise/stop for further spatial development.
The [surface triage](SURFACE_TRIAGE.md) keeps the adapter comparison and fixture
producers in developer tooling and the reports in evidence; it authorizes no
automatic cleanup or new implementation.
