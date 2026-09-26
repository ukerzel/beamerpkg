# beamerpkg

`beamerpkg` is a small experiment in making multimedia Beamer presentations
portable without replacing Beamer's rendering model.

The premise is deliberately narrow:

```text
Beamer -> ordinary PDF + external MP4 files -> one relocatable .beamerpkg
                                               |
                                               v
                                   unpack temporarily + pdfpc
```

Equations, TikZ, columns, backgrounds, arrows, Beamer overlays, fonts, and all
other slide layout remain PDF. The package layer only restores external media at
the relative paths already referenced by the PDF.

## MVP

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

## Authoring

Add the small helper package to TeX's search path and use `\pkgmovie` where a
normal Beamer `\movie` would be used:

```latex
\usepackage{beamerpkg}

\pkgmovie[loop,showcontrols]
  {\includegraphics[width=\linewidth]{media/poster.png}}
  {media/simulation.mp4}
```

The macro delegates the actual PDF movie annotation and geometry to Beamer's
`multimedia` package. It additionally records `media/simulation.mp4` in
`<jobname>.beamerpkg-assets`.

## Package

If the PDF, asset list, and media are rooted in the same directory:

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

With `pdfpc` installed:

```bash
poetry run beamerpkg present talk.beamerpkg
```

`beamerpkg` validates the archive, extracts it to a temporary directory while
preserving all relative paths, launches `pdfpc` from that directory, and keeps
the directory alive until the presenter exits.

## Demo

The demo intentionally mixes equations, TikZ, columns, overlays, and video.
A repository-friendly H.264 transcode of the supplied 1280x720 test video and a poster frame are committed under `examples/media/`. Build the PDF/package with:

```bash
./examples/build_demo.sh
```

Then copy **only** `examples/demo.beamerpkg` elsewhere and run it with pdfpc.
That relocation test is the core MVP acceptance criterion.

See [`docs/MVP.md`](docs/MVP.md) for the scope and acceptance test.
