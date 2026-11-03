# Current status

Updated 2026-11-03. The spatial route is merged into `main`; the reviewed fixes
and expanded tests were committed and pushed as `f1db522`. Documentation and
release preflight were pushed as `279d545`. The user then authorized version
1.3.0, the GitHub tag and PyPI publication. Version metadata is now 1.3.0.

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
the documented Linux/Chromium scope.

## Release 1.3.0

The release retains the v1 container format and existing commands. The final
wheel and sdist are built with bundled frontend assets, checked with strict
Twine validation and installed outside the checkout before publication. The
sdist must also rebuild a matching wheel without Node. Checks are documented in
[CONTRIBUTING](../CONTRIBUTING.md) and the
[frontend guide](../frontend/spatial/README.md).

Final files are selected by exact versioned filename from `dist/`; older
releases in that directory are not included in the upload. PyPI does not allow
reusing published filenames; see its
[upload troubleshooting](https://docs.pypi.org/publishing/troubleshooting/#why-am-i-getting-a-filename-or-contents-already-exists-or-filename-has-been-previously-used-error).

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
