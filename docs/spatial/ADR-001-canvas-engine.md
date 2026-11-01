# ADR-001: DOM viewport for the first spatial MVP

Status: accepted for S3 on 2026-11-01, based on
[the Gate 0 probe](GATE0_REPORT.md).

Both React Flow 12.12.0 and a translated/scaled DOM viewport render the
40-page fixture and preserve one active video's element and playback during
camera changes. Both pass the known cropped/rotated coordinate fixture.
Neither is selected as a statistically faster renderer; the observed timings
include shared/uncontrolled caches.

Choose a single DOM viewport for production. The current consumer needs
PDF surfaces, a semantic camera and media placement, with no graph edges or
node editing in this first slice. Direct transforms keep presenter keyboard
and animation lifetime under the navigation controller without additional
graph interaction rules. React remains useful for controls and stable content
components; React Flow is a developer probe dependency only.

Cost: we own a small pan/zoom/cancelable-camera implementation. Verify actual
pointer behavior, interruption, reduced motion, resize and key handling in S3.
Keep media lifetime independent of resolution changes. Do not create a generic
canvas adapter framework or ship both engines. Reconsider only if measured
editing/interaction needs justify that later; no editor is included now.
