# Reviewing

Review against the MVP claim, not against hypothetical future features.

Check that changes:

1. preserve Beamer/PDF as the slide renderer;
2. preserve media paths exactly inside the package;
3. reject path traversal and undeclared/tampered package contents;
4. do not add dependencies or abstractions without a concrete requirement;
5. include tests that would fail for the regression being addressed;
6. keep the package readable as an ordinary ZIP archive.

A change that broadens the scope should include the corresponding rationale in
`docs/MVP.md`.

For the feature-branch spatial experiment, also review against
`docs/SPATIAL_MVP.md` and `issues.md` Active Batch. PDF.js is the additional
route's renderer, not a change to pdfpc. Require independent route selection,
bounded archive/render work, read-only allowlisted serving, original PDF/media
bytes, correct coordinates, deterministic navigation/media lifetime, and
installed-wheel offline evidence. Do not equate software tests, buffer counts,
or screenshot capture with live pdfpc rendering or human lecture acceptance.
