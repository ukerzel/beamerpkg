# Next steps after the MVP

The MVP established that a ZIP-based container can make an external-media Beamer
PDF relocatable without replacing Beamer/PDF rendering.

The remaining work should stay incremental.

## 1. Next spike: wrapperless media discovery

### Goal

Allow a conventional Beamer document such as

```latex
\usepackage{multimedia}

\movie[loop,showcontrols]
  {\includegraphics[width=\linewidth]{media/poster.jpg}}
  {media/video.mp4}
```

to be packaged with:

```bash
beamerpkg pack talk.pdf --root .
```

without `beamerpkg.sty` and without a `.beamerpkg-assets` sidecar.

### Proposed approach

Read PDF annotations during `pack` and collect only standard external movie
references. For the MVP-generated PDF, the relevant structure is a movie
annotation whose file specification contains a relative `/F` path such as:

```text
/F (media/video.mp4)
```

Resolve those paths against `--root`, retain the same fail-closed traversal
checks used by the current sidecar route, deduplicate them, and package them at
the identical archive paths.

### Compatibility

Keep the current explicit `--assets` / sidecar route temporarily as a fallback
until the PDF-discovery route has an end-to-end test. Do not create two
independent packaging implementations; both routes should feed the same validated
asset-path pipeline.

### Completion evidence

- an unmodified standard Beamer `\movie` demo packages successfully;
- no `beamerpkg.sty` is required for that demo;
- the generated package passes the existing relocation/integrity tests;
- the real pdfpc click-to-play test still works;
- malformed, absolute, remote, and path-traversing references fail clearly or
  are explicitly classified as unsupported.

## 2. Presenter ergonomics

After wrapperless packing, allow presenter arguments to pass through without
inventing platform-specific policy, for example:

```bash
beamerpkg present talk.beamerpkg -- -S -w both
```

This is useful for rehearsal, WSL/WSLg, and unusual display setups while keeping
pdfpc responsible for presentation semantics.

## 3. Autoplay

Treat autoplay as a separate viewer-capability experiment. The validated
container does not need autoplay to work, and pdfpc's standard movie-annotation
behavior is click-to-play. Do not encode autoplay hacks into the container
format unless a portable viewer mechanism is demonstrated.

## 4. Desktop/file association

Only after the CLI and wrapperless path are stable, add convenience integration
such as associating `.beamerpkg` with a tiny launcher on Linux/macOS/Windows.
This should remain a shell around the same package validation/extraction code,
not become a second application architecture.

## Non-goals carried forward

- HTML/reveal.js rendering;
- custom PDF renderer;
- custom video player;
- PowerPoint/Keynote import/export;
- speculative package metadata without a concrete consumer.
