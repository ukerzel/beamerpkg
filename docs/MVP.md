# MVP design and result

This document preserves the original 2026-09-30 experiment and subsequent
requirements/decisions. The original questions and next steps below are
historical. Use [README](../README.md) and the
[spatial guide](spatial/USER_GUIDE.md) for current commands and support limits.

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

`beamerpkg.sty` (now `src/beamerpkg/tex/beamerpkg.sty`) provides `\pkgmovie`. It delegates layout and annotation
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

## Distribution (1.0.1)

Requirement: a `pip install beamerpkg` user must be able to use
`\pkgpdfpcmovie` for pdfpc autoplay. Before 1.0.1 the helper lived only in the
repository's `tex/` directory and was absent from the wheel, so PyPI users could
pack and present but not author autoplay slides.

Minimal extension: `beamerpkg.sty` moves into the Python package as package
data, and `beamerpkg texdir` prints its directory for `TEXINPUTS`. No LaTeX
installation step, TDS layout, or configuration is introduced.

## Media-optional packing

Requirement: talks without video must still be bundled as one `.beamerpkg`
(PDF, `.pdfpc` notes, editable source). Previously `pack` failed with "no
supported external media references found" and rejected empty asset lists, so
media-free talks could not use the container at all.

Minimal change: when neither PDF discovery, `--assets`, nor the legacy sidecar
yields media, `pack` produces a package with `"assets": []`. The schema is
unchanged; `inspect` and `present` already accepted empty asset lists.

## Optional spatial presentation experiment (2026-11-01)

Requirement: explore a scientific talk through spatial frame groups, detail
views, and reversible detours while preserving its PDF/media content. This is
an additional presentation route; pdfpc remains independently supported.

On `feat/spatial-prototype`, the user authorized the bounded read-only first
MVP in [SPATIAL_MVP.md](SPATIAL_MVP.md): local PDF.js canvas, standard browser
video overlays, safe read-only loopback serving, and optional validated layout
JSON. The original container claim and history above remain unchanged. Each
talk may use pdfpc, spatial, or both; no migration or dual authoring is required.
No full editor, write API, schema change, release, or merge is included.

### Presentation polish after first look (2026-11-02)

Finding: the user reported that the spatial viewer works technically but feels
uninspiring to present with. Bounded response, frontend only: smooth
zoom-out/pan/zoom-in camera paths, auto-hiding presentation chrome, dimmed
non-active frames, an overview route with numbered step jumps, a minimap,
viewpoint previews cropped from existing thumbnails, a shortcut sheet,
PgUp/PgDn clicker keys, fullscreen, and an overlay crossfade that holds the
previous sharp render until the next is ready. PDF pages remain unchanged
PDF.js renders; no Python, archive, sidecar schema, server, or pdfpc change.
Canvas accounting stays below 128 MiB (thumbnail budget scaled by deck size).

### Demo talk on the spatial route (2026-11-02)

Finding: the synthetic science fixture made the spatial route look weak
next to the polished pdfpc demo. Response: `examples/demo.beamerpkg` now also
gets an authored spatial layout, generated by `tools/demo_spatial_layout.py`
during `build_demo.sh` and bound to that build's PDF hash. The deck's wording
names both routes (title subtitle, an added `spatial` command on "Try it"). Its
page count and overlay structure are unchanged, so the pdfpc route, notes and
sidecar behave as before. The science fixture remains the automated test input.

### Backup material in the demo talk (2026-11-03)

Requirement: talks usually carry backup frames for questions, and on the
spatial route these should sit apart from the main track, grouped visibly by
topic. Response: `demo.tex` gains three backup parts after `\appendix`
(appendixnumberbeamer and pdfpc `enduserslide=11` keep the main talk's frame
count and progress unchanged). The generated layout places each part as a tight
cluster in a band below the talk, adds a world-rectangle viewpoint per part
and a `backup` path. No schema change is involved: the clusters come from
placement alone. The viewer only gains miniature previews of canvas-region
viewpoints, drawn from the existing thumbnails.

### Merge into main (2026-11-03)

Decision: the user walked through the demo talk on the spatial route and asked
for an audit and merge. A review of the whole branch reported ten findings.
Seven were verified as real and fixed with regression tests (`b995141`):
- runtime 404s under a symlinked temp dir;
- a restored video pausing or rewinding after a later pan;
- overview framing taking the current step's padding;
- a missing MediaBox.top clamp;
- tracebacks from malformed page values;
- launch-target normalization differing from `pack`;
- a thumbnail render-key collision.

The pdfpc route is unchanged and independent. The spatial route stays optional
and read-only, and is not yet in a PyPI release.

### Packaging capabilities and release-review corrections (2026-11-03)

The implemented container requirements also include wrapperless media discovery,
optional media, automatic or explicitly selected pdfpc notes, and selected
editable source files/directories under `source/`. Sources are explicit snapshots;
automatic LaTeX dependency discovery and rebuilding remain outside scope.

The release review corrected input-file overwrites, archive path/member
collisions, explicit notes naming, malformed-input errors, PDF false-control
decoding, relative media normalization and symlinked source parents. It added
regressions and expanded validation to 208 Python tests, with the existing 27
frontend tests and installed-wheel proof passing. The archive schema remains v1.
See [WORKLOG](../WORKLOG.md) for evidence and the
[CLI/media reference](../README.md) for the resulting behavior.
