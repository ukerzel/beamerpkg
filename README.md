# beamerpkg

`beamerpkg` makes multimedia Beamer presentations portable without replacing
Beamer's rendering model. One archive can be presented through two first-class
routes: pdfpc, usually the main one, and a spatial canvas. Neither route requires
the other, and every package must work on both.

```text
Beamer -> ordinary PDF + external MP4 files -> one relocatable .beamerpkg
                                               |
                          +--------------------+--------------------+
                          v                                         v
            beamerpkg present (pdfpc)                beamerpkg spatial (canvas)
            two screens, notes, timer                zoomable canvas in a browser
```

Equations, TikZ, columns, backgrounds, arrows, Beamer overlays, fonts, and all
other slide layout remain PDF. The package layer only restores external media at
the relative paths already referenced by the PDF.

## Status

The container/path MVP was validated on **2026-09-30** with pdfpc under WSL/WSLg:
the packaged PDF rendered normally and the packaged H.264 video played in the
TeX-defined rectangle. The full-resolution autoplay demo also works.

Version 0.2 added **wrapperless media discovery**: for standard Beamer
`multimedia/\movie` documents, `beamerpkg pack` reads the PDF annotation and
collects the referenced local media automatically. A `.beamerpkg-assets`
sidecar is no longer required for normal use.

Version 1.2.0 made media optional. A PDF without movie references packs as
PDF-only (plus the `.pdfpc` notes and `--source` payload, if any), with an empty
`assets` list.

Version 1.3.0 adds the spatial presentation route, bundled offline browser
resources, and the packaging/media fixes described below. The pdfpc route and
v1 archive format remain supported. See the
[1.3.0 tag](https://github.com/ukerzel/beamerpkg/tree/v1.3.0).

### Two presentation routes

The same `.beamerpkg` supports both routes. Both are first-class, though pdfpc
will usually be the main one:

```bash
beamerpkg present talk.beamerpkg   # pdfpc: two screens, speaker notes, timer
beamerpkg spatial talk.beamerpkg   # spatial: the slides on a zoomable canvas
```

Pick a route per talk, or use both with the same archive. Neither depends on
the other: `present` needs no browser, layout or frontend tooling, and `spatial`
needs no pdfpc. A change to packing, the archive or media discovery has to keep
both routes working.

The spatial route shows the unchanged PDF on a canvas. It supports explicit
overlay groups, whole-frame and detail viewpoints, guided paths, exploring and
returning, and both packaged-video forms. A spatial arrangement lives beside the
archive in `talk.spatial.json`; the archive format is the same for both routes.
Spatial is read-only for now: there is no graphical editor or write API yet.

From a checkout, build the pinned frontend before using `spatial`, following
the setup below. Built wheels include its offline assets and need no end-user
Node/npm or pdfpc. `examples/build_demo.sh` builds the demo talk for both routes. See the
[try-it guide](https://github.com/ukerzel/beamerpkg/blob/main/docs/spatial/USER_GUIDE.md),
[first-MVP contract](https://github.com/ukerzel/beamerpkg/blob/main/docs/SPATIAL_MVP.md), and
[technical evaluation](https://github.com/ukerzel/beamerpkg/blob/main/docs/spatial/PROTOTYPE_EVALUATION.md).

The viewer includes grouped overlays, whole-frame and detail views, named
paths, a whole-canvas overview with clickable steps, a minimap, viewpoint
previews, fullscreen and keyboard/clicker controls. Temporary detours retain
the guided position; nested returns restore overlays, camera and paused media.
The demo includes separate backup clusters for questions. See the guide for
the controls, supported media options and size limits.

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

The manifest contains SHA-256 hashes and byte sizes. Runtime media are restored
at the relative locations used by Beamer; harmless `./` and repeated path
separators are normalized without changing the PDF. Optional editable sources
live under `source/` and are recorded separately in the manifest.

## Install the released package

```bash
python -m pip install beamerpkg
beamerpkg present talk.beamerpkg
```

Version 1.3.0 includes both presentation routes. Use
`beamerpkg spatial talk.beamerpkg` for the spatial viewer; no Node/npm is
needed when installing the published wheel.

## Install for development

Requires Python 3.11+ and Poetry. To present through pdfpc, install pdfpc and
the system codecs required by your media. Python packing and inspection do
not need pdfpc, TeX or Node.

```bash
poetry install
```

The only runtime Python dependency is `pypdf`, used to inspect PDF annotations.

For spatial presentation from a checkout, also install Node 22.13+ and npm
(as required by the pinned frontend dependencies) and build the bundled frontend:

```bash
(cd frontend/spatial && npm ci && npm run build)
```

Built wheels include these resources. End users of a built wheel need a browser
for spatial presentation, but no Node/npm. Building the example PDFs requires
a TeX installation with Beamer, TikZ/PGFPlots, `slashed`, `pdfpc` and
`appendixnumberbeamer`; the video and poster are already included.

## CLI reference

Run `beamerpkg COMMAND --help` for command-specific help.

| Command | Options and behavior |
|---|---|
| `pack PDF` | `--root DIR` sets the media root (default: PDF directory); `--output PATH` / `-o PATH` selects the archive (default: PDF stem plus `.beamerpkg`). |
| `pack PDF --assets FILE` | Uses an explicit asset list instead of discovering PDF media. |
| `pack PDF --notes FILE` | Selects notes explicitly; otherwise includes a same-stem `.pdfpc` file beside the PDF when present. |
| `pack PDF --source PATH` | Repeat to include editable files/directories relative to `--source-root DIR` (default: media root). |
| `inspect ARCHIVE` | Validates the archive and prints its inventory; `--json` prints the validated manifest. |
| `present ARCHIVE` | Extracts temporarily and launches pdfpc; `--presenter EXECUTABLE` selects another executable. Arguments after `--` are passed to the presenter. |
| `spatial ARCHIVE` | Starts the local viewer; `--no-browser` prints the URL without opening a browser. |
| `texdir` | Prints the installed directory containing `beamerpkg.sty`. |

`pack` prints the output path. Recognized package-validation errors print a
message on stderr and return status 2. `present` returns the presenter's exit
status and removes its temporary extraction when the subprocess exits.

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
symlinks are rejected, including symlinked parent directories within a selected
path. This is a selected source snapshot; dependencies are not discovered and
the source is not rebuilt automatically.

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

The asset list contains one path per line, relative to the media root. Blank
lines and lines starting with `#` are ignored; repeated paths are collapsed.
Selection order is explicit `--assets`, then PDF discovery, then a same-stem
`.beamerpkg-assets` fallback if discovery found no media. An empty explicit
list is accepted. Supported references to missing or unsafe files still fail.

| Annotation | Packing | Spatial playback |
|---|---|---|
| Standard `/Movie` | Discovers a string or `/UF` / `/F` file specification. | Uses the annotation rectangle; accepts `/Mode /Once` or `/Repeat` and boolean `/ShowControls`. Missing flags remain unknown. |
| pdfpc `/Link` + `/Launch` | Discovers the file before `?` when options include `autostart`, `loop`, `start` or `stop`. Unrelated launch actions are ignored. | Supports `autostart` and `loop` only, without values or duplicates. Other encoded options fail visibly. |

Spatial playback also requires a visible, nonempty rectangle and a declared
local asset. Embedded media and arbitrary PDF action execution are unsupported.
Browser codec and autoplay policies still apply; see the
[media and support limits](https://github.com/ukerzel/beamerpkg/blob/main/docs/spatial/USER_GUIDE.md#media-and-support-limits).

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

Use `--notes path/to/selected-notes.json` to select another notes file. Its bytes
are restored as `talk.pdfpc`, matching the presentation name so pdfpc can find it.
Provide a pdfpc-compatible notes file; packing does not convert its contents.

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

## Validation and recent fixes

Packing rejects unsafe paths, source symlinks, duplicate member names,
file/directory collisions and output paths that would overwrite selected inputs.
Archive validation checks declared sizes and hashes and rejects undeclared
files, noncanonical manifest paths and ZIP symlinks. A failed archive write
keeps an existing output bundle and removes temporary output.

The release-preparation fixes also preserve explicit notes under the PDF stem,
decode `/ShowControls false` correctly, align relative media-path normalization
between routes, and turn the tested malformed ZIP/PDF/layout cases into readable
errors. The 2026-11-03 check passed 208 Python tests and 27 frontend tests;
Python coverage was 98.25% for statements and 95.39% for branches. This is
software validation on Python 3.14.4/Chromium, not a broader platform claim.
See [contributor checks](https://github.com/ukerzel/beamerpkg/blob/main/CONTRIBUTING.md) and the [review record](https://github.com/ukerzel/beamerpkg/blob/main/WORKLOG.md).

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

After installing the Python dependencies, TeX packages and (for spatial use)
building the frontend, build both demo archives:

```bash
./examples/build_demo.sh

poetry run beamerpkg present examples/demo.beamerpkg
poetry run beamerpkg present examples/wrapperless.beamerpkg
poetry run beamerpkg spatial examples/demo.beamerpkg
```

This script regenerates the example PDFs/packages and writes
`examples/demo.spatial.json`. To transport the authored demo, copy that sidecar
with `demo.beamerpkg`; pdfpc needs only the archive. For isolated developer
fixtures that preserve example outputs, run
`poetry run python tools/build_spatial_fixtures.py`.

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

## Documentation

- [Spatial user guide](https://github.com/ukerzel/beamerpkg/blob/main/docs/spatial/USER_GUIDE.md): setup, demo, controls,
  current sidecar schema and support limits.
- [Contributing](https://github.com/ukerzel/beamerpkg/blob/main/CONTRIBUTING.md) and [frontend development](https://github.com/ukerzel/beamerpkg/blob/main/frontend/spatial/README.md):
  Python/browser checks and installed-distribution verification.
- [Current status and release preparation](https://github.com/ukerzel/beamerpkg/blob/main/docs/NEXT_STEPS.md): completed work,
  release steps and deferred scope.
- [MVP history](https://github.com/ukerzel/beamerpkg/blob/main/docs/MVP.md), [first spatial contract](https://github.com/ukerzel/beamerpkg/blob/main/docs/SPATIAL_MVP.md),
  [broader design](https://github.com/ukerzel/beamerpkg/blob/main/docs/SPATIAL_PLAN.md) and dated spatial reports: decisions
  and evidence at their recorded stages. The broader editor/save design is
  not the implemented feature set.
