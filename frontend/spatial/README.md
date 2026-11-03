# Spatial frontend development

This package contains the spatial viewer merged into `main` and a developer-only
adapter comparison. Node/npm build the app; installed runtime commands use
the bundled assets and do not need them.

The pinned dependencies require Node 22.13+; the current build was checked
with Node 24.13.0 and npm 11.21.1.

From the repository root, set up Python and build isolated real PDF/package
fixtures. This requires the TeX environment and committed demo media listed in
[README](../../README.md#install-for-development); it preserves example outputs.

```bash
poetry install
poetry run python tools/build_spatial_fixtures.py
```

Then in `frontend/spatial`:

```bash
npm ci
node scripts/resources.mjs --dev
PLAYWRIGHT_BROWSERS_PATH=/tmp/beamerpkg-browsers npx playwright install chromium
npm run typecheck
npm run build
PLAYWRIGHT_BROWSERS_PATH=/tmp/beamerpkg-browsers npm test
```

In the restricted workspace, use `npm --cache /tmp/beamerpkg-npm-cache ...`
to keep npm's cache in a writable directory. Browser binaries, node_modules,
probe PDFs/media, and test traces stay out of Git.

`probe.html?adapter=dom` and `probe.html?adapter=flow` compare the same actual
40-page repeated-content PDF and one playing media element. React Flow is
developer-only. Run `npm run build` before viewer tests: `npm test` starts a
development server for the adapter probes, while viewer tests launch the
Python server with the already-built production assets. The probe and fixture
content are excluded from the production build. `scripts/resources.mjs` adds local PDF.js resources
and runtime third-party license notices to the Python package static directory.

After these checks, return to the repository root to verify a distribution:

```bash
cd ../..
poetry build --output build/spatial-dist
PLAYWRIGHT_BROWSERS_PATH=/tmp/beamerpkg-browsers poetry run python tools/check_spatial_distribution.py
```

The checker expects the versioned wheel/sdist in `build/spatial-dist`, a pypdf
wheel matching the active Poetry environment in Poetry's artifact cache, and
the installed Chromium above. It installs outside the checkout without an
index, runs both routes, and records hashes/results under
`build/spatial-evidence/s4`. The installed runtime has no Node/npm/pdfpc on PATH;
the external test driver still uses Node and Playwright. Browser requests
outside the exact local endpoint are blocked; this is not OS network isolation.

Generated frontend assets must be rebuilt from the current lockfile after
switching branches. Do not copy bundles from another branch into a release.
See the historical [Gate 0 report](../../docs/spatial/GATE0_REPORT.md) and
[ADR-001](../../docs/spatial/ADR-001-canvas-engine.md) for the adapter decision,
and the [current user guide](../../docs/spatial/USER_GUIDE.md) for controls and limits.
