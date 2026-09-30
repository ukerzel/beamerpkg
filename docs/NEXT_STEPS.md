# Next steps after wrapperless discovery

The core path is now:

```text
ordinary Beamer \movie
        ↓
PDF /Movie annotation
        ↓
beamerpkg pack discovers local media
        ↓
relocatable .beamerpkg
        ↓
pdfpc
```

The legacy `.beamerpkg-assets` route remains only as an explicit/fallback
compatibility path.

## Completed: presenter argument passthrough

Arguments after `--` are forwarded verbatim to pdfpc before the extracted PDF
filename. For example, a one-monitor setup can request both pdfpc windows with:

```bash
beamerpkg present talk.beamerpkg -- -w both
```

This keeps display policy in pdfpc while preserving `.beamerpkg` as the launch
artifact.

## 1. Autoplay compatibility

The current demo has a working pdfpc-specific autoplay path:

```latex
\pkgpdfpcmovie[autostart&loop]{poster}{media/video.mp4}
```

The packer recognizes the resulting `/Launch` action only when it carries known
pdfpc media options (`autostart`, `loop`, `start`, or `stop`). Unrelated
PDF launch actions are ignored rather than packaged.

Keep this separate from standard `\movie`: autoplay is a viewer capability,
not a container property.

## 2. Desktop/file association

After the CLI stabilizes, associate `.beamerpkg` with a thin launcher on
Linux/macOS/Windows. This should call the same validation/extraction code rather
than introduce a second application architecture.

## 3. Packaging/release polish

- generate and commit a Poetry lock file from a Poetry-enabled development
  machine;
- add CI for pytest/Ruff/mypy and the synthetic PDF tests;
- decide whether the legacy sidecar helper should eventually be deprecated;
- document supported PDF annotation forms as a small versioned compatibility
  contract.

## Non-goals carried forward

- HTML/reveal.js rendering;
- custom PDF renderer;
- custom video player;
- PowerPoint/Keynote import/export;
- packaging arbitrary PDF `/Launch` targets;
- speculative package metadata without a concrete consumer.
