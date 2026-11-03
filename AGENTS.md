# AGENTS.md

This repository follows the workflow conventions of `ukerzel/Template-`.

## Project boundary

The current objective is a minimal proof that a Beamer PDF plus external media
can be transported as one relocatable container and presented through `pdfpc`
without changing Beamer/PDF rendering.

Use the smallest implementation sufficient to test that claim. Do not add HTML
rendering, a custom PDF renderer, a custom video player, PDF annotation parsing,
a GUI, transcoding, or generalized configuration unless a concrete MVP failure
requires it. The optional spatial route below is the one accepted exception; its
permissions do not extend to the pdfpc route.

## Development rules

- Python >= 3.11; manage the environment and developer dependencies with Poetry.
- Keep runtime dependencies empty unless a dependency is necessary for an
  accepted requirement.
- Use the `src/` layout.
- Prefer TDD for behavioral changes; tests must target real failure modes rather
  than coverage for its own sake.
- Run the narrowest relevant tests first, then the full test suite.
- Keep public behavior explicit and paths fail-closed: package inputs must not
  escape the declared project root or extraction directory.
- Preserve the normal Beamer/PDF path. Continuous media is an overlay concern,
  not a reason to re-render slides.

## Current non-goals

- autoplay workarounds;
- embedded media inside PDF;
- HTML/reveal.js export;
- automatic `/Movie` annotation discovery;
- Windows/macOS integration;
- packaging LaTeX source;
- PowerPoint/Keynote compatibility.

Before extending scope, update `docs/MVP.md` with the concrete failure or
requirement that justifies the extension.

## Optional spatial route

Built on `feat/spatial-prototype` through S0–S4 of `docs/SPATIAL_MVP.md`
(authorized 2026-11-01). After the user's own walkthrough, the user merged it
into `main` on 2026-11-03. The concrete requirements are recorded in
`docs/MVP.md`; preserve its history. For this route only, the following are
permitted: PDF.js browser rendering of unchanged PDF content, the opt-in
`spatial` command, per-annotation placement inspection, a bounded read-only
loopback server, and pinned local frontend dependencies and resources. These
permissions do not change the existing pdfpc route or its acceptance.

Keep `pack`, `inspect`, and `present` independent of spatial metadata, browser
tooling, and spatial initialization. Spatial needs no pdfpc. Each talk may use
either route or both. Still out of scope without a new recorded requirement:
a full editor, a writable API, a custom PDF or video renderer, a transcoder, an
archive schema change, and a release.
