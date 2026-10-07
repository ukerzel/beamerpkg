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
├── media/
│   └── simulation.mp4
└── source/             # optional editable source snapshot
    ├── talk.tex
    ├── figures/
    └── references.bib
```

The manifest contains SHA-256 hashes and byte sizes. Runtime media are stored at
exactly the same relative paths used by Beamer. Optional editable sources live
under `source/` and are recorded separately in the manifest.

## Install for development

Requires Python 3.11+ and Poetry.

```bash
poetry install
```

The only runtime Python dependency is `pypdf`, used to inspect PDF annotations.

## Optional editable source payload

A presentation package can also carry the LaTeX source and authoring assets so
the recipient can modify and rebuild the presentation without editing the PDF.

Source inclusion is explicit. Pass a source root and repeat `--source` for the
files or directories to preserve:

```bash
poetry run beamerpkg pack build/talk.pdf \
  --root build \
  --source-root . \
  --source talk.tex \
  --source figures \
  --source references.bib
```

Those files are stored with their relative structure under `source/`:

```text
source/
├── talk.tex
├── figures/
│   └── plot.png
└── references.bib
```

Because `.beamerpkg` is an ordinary ZIP archive, a recipient can unpack it,
edit the source tree, and rebuild with their normal LaTeX toolchain. Runtime
presentation files remain separate, so including sources never changes pdfpc
playback.

The source snapshot is deliberately opt-in and explicit: beamerpkg does not
guess which files constitute a reproducible authoring project. Directories are
included recursively; source paths must remain within `--source-root`, and
symlinks are rejected.

An asset needed both by the runtime presentation and by the editable source tree
may be stored twice. This keeps both trees self-contained and avoids symlink or
viewer-specific deduplication behavior in the package format.

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
the bundled LaTeX helper `beamerpkg.sty` provides:

```latex
\pkgpdfpcmovie[autostart&loop]
  {\includegraphics[width=\linewidth]{media/poster.png}}
  {media/video.mp4}
```

The helper ships with the Python package. `beamerpkg texdir` prints its
directory, so LaTeX can find it without copying files:

```bash
TEXINPUTS="$(beamerpkg texdir)//:" pdflatex talk.tex
```

In a repository checkout it lives at `src/beamerpkg/tex/beamerpkg.sty`.

This emits pdfpc's `run:` launch-link mechanism. The packer also recognizes
these pdfpc media launch links and strips their query options when collecting
the underlying media file.

## pdfpc speaker notes and settings

If a same-name pdfpc sidecar exists beside the PDF, it is included automatically:

```text
talk.pdf
talk.pdfpc
```

```bash
poetry run beamerpkg pack talk.pdf --root .
```

The resulting package records `talk.pdfpc` separately as `notes` in the
manifest and restores it beside `talk.pdf` before launching pdfpc. This keeps
speaker notes and other pdfpc presentation metadata portable without putting
them into the PDF itself.

The repository demo contains `examples/demo.pdfpc` with a visible speaker note
on the first page so this behavior can be checked in presenter view.

## Inspect and present

```bash
poetry run beamerpkg inspect talk.beamerpkg
poetry run beamerpkg present talk.beamerpkg
```

`beamerpkg present` validates the archive, extracts it to a temporary directory
while preserving all relative paths, launches `pdfpc` from that directory, and
keeps the directory alive until the presenter exits. Arguments after `--` are
forwarded verbatim to the presenter before the PDF filename.

For a single physical monitor, keep both pdfpc windows available and switch
between presenter and audience views with the desktop window switcher.

When invoking through Poetry, pass pdfpc options directly after the package:

```bash
poetry run beamerpkg present talk.beamerpkg -w both
```

Poetry may consume a literal `--` separator before the Beamerpkg CLI sees it.
When invoking an installed `beamerpkg` executable directly, the explicit
separator form is also supported:

```bash
beamerpkg present talk.beamerpkg -- -w both
```

This is intentionally transparent passthrough rather than a Beamerpkg-specific
single-monitor mode. Other pdfpc options work the same way.

## Demo

The demo uses the full repository assets, a pdfpc metadata sidecar, and an
editable source snapshot:

- `examples/media/gemini_generated_video_b2693757.mp4`
- `examples/media/video-poster_big.png`
- `examples/demo.pdfpc` (speaker notes / pdfpc metadata)
- `source/examples/demo.tex`
- `source/examples/media/...`
- `source/src/beamerpkg/tex/beamerpkg.sty`

The mixed demo also contains two lightweight Beamer/PDF motion examples before
the video slides:

- a short `\transfade[duration=0.2]` page transition;
- a three-state manual overlay sequence that progressively builds
  `Input -> Model -> Result` and remains fully reversible with the arrow keys.

Both are encoded in the PDF itself; `beamerpkg` does not need to discover or
package anything special for them. The overlay example deliberately avoids
`\transduration`: timed PDF pages restart their timer when revisited, which
makes backward navigation jump forward again.

Build both the mixed autoplay demo and a pure stock-Beamer wrapperless example:

```bash
git pull --rebase
poetry install
./examples/build_demo.sh

poetry run beamerpkg present examples/demo.beamerpkg
poetry run beamerpkg present examples/wrapperless.beamerpkg
```

`examples/demo.tex` also embeds speaker notes and a 10-minute countdown via
the standard `pdfpc` LaTeX package, so they travel inside the PDF itself. The
title page deliberately has no embedded note: pdfpc lets an embedded note
replace the sidecar note for the same page, so page 1 keeps showing the
`examples/demo.pdfpc` note and both routes can be checked in presenter view.

`examples/wrapperless.tex` imports only Beamer's `multimedia` package. It is
the integration proof that packaging no longer depends on a Beamerpkg-specific
LaTeX command. In pdfpc this wrapperless example is click-to-start.

The mixed `examples/demo.tex` intentionally contains two video slides: one
standard wrapperless `\movie` slide that is click-to-start, followed by one
pdfpc-specific `\pkgpdfpcmovie[autostart&loop]` slide that starts
automatically.

See [`docs/MVP.md`](https://github.com/ukerzel/beamerpkg/blob/main/docs/MVP.md) for the original acceptance test and
[`docs/NEXT_STEPS.md`](https://github.com/ukerzel/beamerpkg/blob/main/docs/NEXT_STEPS.md) for the remaining work.
