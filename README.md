# beamerpkg

`beamerpkg` makes multimedia Beamer presentations portable without replacing
Beamer's rendering model.

```text
Beamer -> ordinary PDF + external MP4 files -> one relocatable .beamerpkg
                                               |
                                               v
                                   unpack temporarily + pdfpc
```

Equations, TikZ, columns, backgrounds, arrows, Beamer overlays, fonts, and all
other slide layout remain PDF. The package layer only restores external media at
the relative paths already referenced by the PDF.

## MVP status

**Validated on 2026-09-30 with pdfpc under WSL/WSLg.**

The packaged PDF rendered normally and clicking the poster played the packaged
H.264 video in the TeX-defined rectangle. Running the PDF directly through pdfpc
gave the same behavior, confirming that beamerpkg is only the transport/path
layer.

See [`docs/MVP.md`](docs/MVP.md) for the recorded acceptance test and
[`docs/NEXT_STEPS.md`](docs/NEXT_STEPS.md) for the next spike.

## Package format

A `.beamerpkg` is an ordinary ZIP archive:

```text
talk.beamerpkg
├── manifest.json
├── talk.pdf
├── talk.pdfpc          # optional
└── media/
    └── simulation.mp4
```

The manifest contains SHA-256 hashes and byte sizes. Media are stored at exactly
the same relative paths used by Beamer.

## Install for development

Requires Python 3.11+ and Poetry.

```bash
poetry install
```

Runtime code intentionally uses only the Python standard library.

## Current MVP authoring route

The first MVP uses the small helper package `tex/beamerpkg.sty` and
`\pkgmovie` where a normal Beamer `\movie` would be used:

```latex
\usepackage{beamerpkg}

\pkgmovie[loop,showcontrols]
  {\includegraphics[width=\linewidth]{media/poster.png}}
  {media/simulation.mp4}
```

The macro delegates the PDF movie annotation and geometry to Beamer's
`multimedia` package and records the media path in
`<jobname>.beamerpkg-assets`.

The next spike is to discover standard `\movie` references directly from the
PDF so this helper is no longer required.

## Package

```bash
poetry run beamerpkg pack talk.pdf --root .
```

For a build directory:

```bash
poetry run beamerpkg pack build/talk.pdf \
  --assets build/talk.beamerpkg-assets \
  --root . \
  --output talk.beamerpkg
```

Inspect before presenting:

```bash
poetry run beamerpkg inspect talk.beamerpkg
```

## Present

With `pdfpc` and the required GStreamer codecs installed:

```bash
poetry run beamerpkg present talk.beamerpkg
```

The poster is click-to-play with the current pdfpc movie-annotation path.

`beamerpkg` validates the archive, extracts it to a temporary directory while
preserving all relative paths, launches `pdfpc` from that directory, and keeps
the directory alive until the presenter exits.

## Demo

The demo mixes equations, TikZ, columns, overlays, and video. A
repository-friendly H.264 test video and poster are under `examples/media/`.

```bash
./examples/build_demo.sh
poetry run beamerpkg present examples/demo.beamerpkg
```
