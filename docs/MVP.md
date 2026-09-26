# MVP design

## Question being tested

Can an ordinary Beamer PDF that uses external movie annotations be made portable
by bundling the PDF and referenced media into one relocatable container, then
restoring the same relative paths before launching `pdfpc`?

The MVP intentionally does **not** test a new renderer, HTML conversion, PDF
rewriting, automatic PDF annotation parsing, autoplay workarounds, or a custom
media player.

## Data flow

```text
Beamer source
   | pdflatex
   v
PDF + .beamerpkg-assets + media/
   | beamerpkg pack
   v
talk.beamerpkg   (ZIP_STORED)
   | beamerpkg present
   v
temporary directory with original relative paths
   | pdfpc talk.pdf
   v
PDF rendering + pdfpc movie playback
```

## Container schema v1

A `.beamerpkg` file is an ordinary ZIP archive containing:

- `manifest.json`
- one presentation PDF at the archive root
- optionally a same-name `.pdfpc` notes file
- all declared media at exactly the paths referenced from the PDF

`manifest.json` records SHA-256 and byte length for every packaged file.

## LaTeX scope

`tex/beamerpkg.sty` provides `\pkgmovie`. It delegates layout and annotation
creation to Beamer's existing `multimedia` package and additionally writes the
movie path to `<jobname>.beamerpkg-assets`.

The first experiment deliberately does not monkey-patch `\movie`. If the
container idea works, a later spike can inspect `/Movie` annotations directly
and potentially eliminate the LaTeX helper entirely.

## Acceptance test

1. Build `examples/demo.tex` and `examples/demo.beamerpkg`.
2. Copy only `demo.beamerpkg` to an unrelated directory or machine.
3. Remove or rename the original `examples/media/` directory.
4. Run `beamerpkg present demo.beamerpkg` on a system with `pdfpc` and suitable
   GStreamer codecs.
5. Verify ordinary Beamer slides render normally.
6. Verify clicking the poster starts the video in the TeX-defined rectangle.
7. Verify loop/controls behave according to pdfpc.
8. Verify subsequent Beamer overlays still behave normally.

If those conditions hold, the central architecture is validated.
