# S1 — bounded project admission and media/layout contracts

Date: 2026-11-01. Baseline plan: `2fa9f70`.

Commands:

```bash
poetry run pytest tests/test_spatial_project.py tests/test_spatial_model.py tests/test_spatial_media.py -q
poetry run pytest -q
poetry run ruff check .
poetry run mypy src
```

Result: 22 focused tests, 41 total tests passed; Ruff passed; mypy passed for
six source files. Tests initially failed to import the new owner/API, before
implementation. Negative cases cover byte/count/ratio/symlink admission,
source replacement after admission, stale hash, duplicate JSON keys/IDs,
nonfinite values, invalid references/regions/grouping, geometry mismatch,
missing assets/rectangles, remote paths and malformed playback options.

The existing local `examples/demo.beamerpkg` was admitted/extracted without
changing it. Its 26 pages yielded standard movie placement 17/0 with repeat
and controls enabled, and pdfpc placement 18/1 with autostart and loop. Both
reference the same declared MP4 and retain independent annotation rectangles.
This is preserved-artifact inspection, not a fresh TeX/browser qualification.

Old package/CLI implementations are unchanged. The additional placement API
does not alter the old deduplicated discovery function. First-MVP limitations:
nonempty media overrides and playback options beyond the two demo forms are
rejected explicitly; no layout editor/write API exists. Next: fresh fixtures,
pinned browser/PDF.js and adapter comparison in S2.
