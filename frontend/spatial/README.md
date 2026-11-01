# Spatial frontend development

This package contains the first-MVP viewer work and a developer-only adapter
comparison. Python/runtime commands do not require Node; development does.

From repository root, first run `poetry run python tools/build_spatial_fixtures.py`.
It builds isolated real PDFs/packages and generates local probe resources.
Then in this directory:

```bash
npm ci
node scripts/resources.mjs --dev
PLAYWRIGHT_BROWSERS_PATH=/tmp/beamerpkg-browsers npx playwright install chromium
npm run typecheck
PLAYWRIGHT_BROWSERS_PATH=/tmp/beamerpkg-browsers npm test
```

In the restricted workspace, use `npm --cache /tmp/beamerpkg-npm-cache ...`
to keep npm's cache in a writable directory. Browser binaries, node_modules,
probe PDFs/media, and test traces stay out of Git.

`probe.html?adapter=dom` and `probe.html?adapter=flow` compare the same actual
40-page repeated-content PDF and one playing media element. React Flow is
developer-only. `npm run build` is the production build command once the S3
viewer entry exists; the probe and generated fixture content are excluded
from the production build. `scripts/resources.mjs` adds local PDF.js resources
and runtime third-party license notices to the Python package static directory.

See `docs/spatial/GATE0_REPORT.md` and ADR-001 for evidence and limitations.
