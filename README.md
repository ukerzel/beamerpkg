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

## Status

The container/path MVP was validated on **2026-09-30** with pdfpc under WSL/WSLg:
the packaged PDF rendered normally and the packaged H.264 video played in the
TeX-defined rectangle. The full-resolution autoplay demo also works.

Version 0.2 adds **wrapperless media discovery**: for standard Beamer
`multimedia/\movie` documents, `beamerpkg pack` reads the PDF annotation and
collects the referenced local media automatically. A `.beamerpkg-assets`
sidecar is no longer required for normal use.

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

The only runtime Python dependency is `pypdf`, used to inspect PDF annotations.

## Standard Beamer: no Beamerpkg LaTeX helper required

The wrapperless standard-Beamer route is **click-to-start in pdfpc**. This is
the expected behavior of the normal `\movie` annotation path; autoplay is a
separate pdfpc-specific feature described below.

Write an ordinary Beamer movie:

```latex
\usepackage{multimedia}

\movie[loop,showcontrols]
  {\includegraphics[width=\linewidth]{media/poster.png}}
  {media/video.mp4}
```

Compile it normally, then package it:

```bash
poetry run beamerpkg pack talk.pdf --root .
```

The packer discovers the external `/Movie` file reference from the PDF,
validates that it is a safe local relative path, and includes it at the same path
inside the container.

An explicit sidecar remains available as a compatibility/fallback route:

```bash
poetry run beamerpkg pack talk.pdf --root . --assets talk.beamerpkg-assets
```

## pdfpc autoplay

Autoplay is viewer-specific rather than part of the container format. For pdfpc,
`tex/beamerpkg.sty` provides:

```latex
\pkgpdfpcmovie[autostart&loop]
  {\includegraphics[width=\linewidth]{media/poster.png}}
  {media/video.mp4}
```

This emits pdfpc's `run:` launch-link mechanism. The packer also recognizes
these pdfpc media launch links and strips their query options when collecting
the underlying media file.

## Inspect and present

```bash
poetry run beamerpkg inspect talk.beamerpkg
poetry run beamerpkg present talk.beamerpkg
```

`beamerpkg present` validates the archive, extracts it to a temporary directory
while preserving all relative paths, launches `pdfpc` from that directory, and
keeps the directory alive until the presenter exits.

## Demo

The demo uses the full repository assets:

- `examples/media/gemini_generated_video_b2693757.mp4`
- `examples/media/video-poster_big.png`

Build both the mixed autoplay demo and a pure stock-Beamer wrapperless example:

```bash
git pull --rebase
poetry install
./examples/build_demo.sh

poetry run beamerpkg present examples/demo.beamerpkg
poetry run beamerpkg present examples/wrapperless.beamerpkg
```

`examples/wrapperless.tex` imports only Beamer's `multimedia` package. It is
the integration proof that packaging no longer depends on a Beamerpkg-specific
LaTeX command. In pdfpc this wrapperless example is click-to-start.

The mixed `examples/demo.tex` intentionally contains two video slides: one
standard wrapperless `\movie` slide that is click-to-start, followed by one
pdfpc-specific `\pkgpdfpcmovie[autostart&loop]` slide that starts
automatically.

See [`docs/MVP.md`](docs/MVP.md) for the original acceptance test and
[`docs/NEXT_STEPS.md`](docs/NEXT_STEPS.md) for the remaining work.
