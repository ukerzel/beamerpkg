# AGENTS.md

This repository follows the workflow conventions of `ukerzel/Template-`.

## Project boundary

The current objective is a minimal proof that a Beamer PDF plus external media
can be transported as one relocatable container and presented through `pdfpc`
without changing Beamer/PDF rendering.

Use the smallest implementation sufficient to test that claim. Do not add HTML
rendering, a custom PDF renderer, a custom video player, PDF annotation parsing,
a GUI, transcoding, or generalized configuration unless a concrete MVP failure
requires it.

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
