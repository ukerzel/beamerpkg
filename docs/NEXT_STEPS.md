# Current status and release preparation

Updated 2026-11-03. The spatial route is merged into `main`; the reviewed fixes
and expanded tests were committed and pushed as `f1db522`. Package metadata
still says 1.2.0. A new public release has not been made.

## Implemented

- PDF-only and multimedia `.beamerpkg` archives, optional pdfpc notes, and
  explicitly selected editable source snapshots.
- Standard Beamer `/Movie` and recognized pdfpc `/Launch` media discovery;
  explicit asset lists and the legacy same-stem fallback remain supported.
- Independent `present`/pdfpc and `spatial` commands. Spatial provides grouped
  overlays, detail/world viewpoints, named paths, exploration/return, backup
  clusters, overview step jumps, minimap, previews and keyboard/clicker controls.
- Read-only adjacent layouts bound to the exact PDF path/hash; bundled offline
  frontend resources and a bounded, allowlisted loopback server.
- Release-review fixes for input overwrites, member/path collisions, notes
  naming, malformed inputs, false video-control flags, media normalization and
  symlinked source parents.

The 2026-11-03 review passed 208 Python tests and 27 frontend tests, static/build
checks and an isolated installed-wheel proof. Python coverage was 98.25% for
statements and 95.39% for branches. Detailed evidence paths and limitations
are recorded in [WORKLOG](../WORKLOG.md).

The follow-up release cold read passed strict Twine metadata/README validation,
an sdist-to-wheel rebuild without Node (identical wheel member bytes), and a
fresh installed-wheel proof. README documentation links are absolute so they
also work on PyPI. No further code or documentation blockers were found within
the documented Linux/Chromium scope. The recommended next version is 1.3.0.

## Release preparation

1. Choose the next package version; the documentation review is complete.
   Update both `pyproject.toml` and `src/beamerpkg/__init__.py` when making
   that change. Replace the pre-release wording in README and the spatial guide
   with the new release's availability before the final build.
2. Follow the Python, frontend and installed-distribution checks in
   [CONTRIBUTING](../CONTRIBUTING.md) and the
   [frontend guide](../frontend/spatial/README.md). Rebuild frontend assets
   before producing the final wheel/sdist.
3. Make the release/tag/publication decision explicitly. The local
   `build/spatial-dist` artifacts used for validation still have version 1.2.0;
   they are not the next release. PyPI does not allow reusing published filenames;
   see its [upload troubleshooting](https://docs.pypi.org/publishing/troubleshooting/#why-am-i-getting-a-filename-or-contents-already-exists-or-filename-has-been-previously-used-error).

## Deferred scope

There is no active implementation ladder after this review. A graphical editor,
writable save API, archive-contained spatial layouts, presenter notes/timer/next
preview, dual-monitor spatial presentation and broader OS/browser qualification
need a separate decision. Desktop/file associations and deprecating the legacy
helper have not been implemented or scheduled.

The [broader spatial design](SPATIAL_PLAN.md) preserves ideas for editor/save
work. It does not describe implemented features or authorize those extensions.
Use the [spatial guide](spatial/USER_GUIDE.md) for the current workflow and
support limits.
