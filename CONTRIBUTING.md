# Contributing

This project uses Poetry and the `src/` layout, following the conventions of
`ukerzel/Template-`.

```bash
poetry install
poetry run pytest
```

For a code change, first identify the behavior or regression being addressed.
Add or modify the smallest test that detects it, make the bounded change, then
run the relevant test and the full suite. Avoid speculative abstractions and
unrelated cleanup.

Useful checks:

```bash
poetry run pytest
poetry run ruff check .
poetry run mypy src
poetry check --lock
```

For a release review, include branch coverage and retain a browsable report:

```bash
poetry run pytest --cov=beamerpkg --cov-branch --cov-report=term-missing \
  --cov-report=html:build/release-review/coverage-html
```

This measures Python coverage. Run the spatial frontend tests and the
installed-distribution proof separately as described in
`frontend/spatial/README.md` and `tools/check_spatial_distribution.py`.

See the [frontend instructions](frontend/spatial/README.md) for fixture building,
browser setup, production builds and the installed-wheel check. Frontend
assets are generated and ignored by Git, so build them before building a wheel
or sdist. Use `poetry build --output build/spatial-dist` for local validation;
the installed proof checks this exact directory. Keep experimental builds
separate from published artifacts in `dist/`.

The example PDFs require the TeX packages listed in [README](README.md).
Live pdfpc checks additionally require pdfpc and suitable system media codecs.
The committed demo video is used directly; no transcoding step is required.
