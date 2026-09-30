# MVP design and result

## Question tested

Can an ordinary Beamer PDF that uses external movie annotations be made portable
by bundling the PDF and referenced media into one relocatable container, then
restoring the same relative paths before launching `pdfpc`?

**Result: yes. The MVP was validated on 2026-09-30.**

The MVP deliberately did **not** introduce a new renderer, HTML conversion, PDF
rewriting, autoplay workarounds, or a custom media player.

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
PDF rendering + click-to-play movie playback
```

## Container schema v1

A `.beamerpkg` file is an ordinary ZIP archive containing:

- `manifest.json`
- one presentation PDF at the archive root
- optionally a same-name `.pdfpc` notes file
- all declared media at exactly the paths referenced from the PDF

`manifest.json` records SHA-256 and byte length for every packaged file.

## LaTeX scope used by the MVP

`tex/beamerpkg.sty` provides `\pkgmovie`. It delegates layout and annotation
creation to Beamer's existing `multimedia` package and additionally writes the
movie path to `<jobname>.beamerpkg-assets`.

This helper was intentionally chosen to isolate the first experiment from PDF
parsing. The validated result now justifies a second spike that reads standard
Beamer movie references from the PDF itself.

## Acceptance test

The test was performed under WSL/WSLg on 2026-09-30.

1. Build `examples/demo.tex` and `examples/demo.beamerpkg`.
2. Run `beamerpkg present examples/demo.beamerpkg`.
3. pdfpc renders the ordinary Beamer PDF.
4. pdfpc detects the movie annotation and resolves the packaged
   `media/video.mp4`.
5. With a suitable GStreamer H.264 decoder installed, clicking the poster plays
   the video in the TeX-defined rectangle.
6. Later Beamer overlays remain normal PDF pages.
7. Running `pdfpc examples/demo.pdf` directly gives the same click-to-play
   behavior, so the package layer is not involved in rendering or video-widget
   semantics.

The first run exposed a missing local H.264 GStreamer decoder. Standalone
GStreamer playback after installing codec support and successful in-pdf playback
confirmed that this was an environment dependency rather than a package-format
failure.

## Conclusion

The central architecture is validated:

```text
Beamer/PDF rendering
+ standard external movie annotation
+ restored relative media path
+ one ZIP-based transport artifact
+ pdfpc playback
```

The next question is no longer whether the container works. It is whether
`beamerpkg pack` can discover the media references from an ordinary Beamer PDF
so authors can keep using standard `\movie` without `\pkgmovie`.
