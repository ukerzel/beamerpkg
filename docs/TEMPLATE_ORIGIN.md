# Template origin

This seed follows the project conventions from:

- repository: `ukerzel/Template-`
- branch: `main`
- inspected head: `701dbd76d6d28a0fcd607e995177857c2ed40ace`
  (`Add minimal-sufficient execution gate`)

Retained conventions include Python >=3.11, Poetry with an in-project virtual
environment, `src/` layout, pytest, Ruff, mypy, Apache-2.0, and explicit
agent/contributing/reviewing guidance.

Project-specific deviations are intentional:

- package mode is enabled because `beamerpkg` installs a CLI;
- the template's literature-review dependency group and workflow machinery are
  omitted because they are unrelated to the MVP;
- agent/review documents are narrowed to the current MVP rather than carrying
  template-maintenance history into the new repository;
- `poetry.lock` was absent when the seed was created because Poetry was
  unavailable in that execution environment. It has been committed since
  1.2.0; use `poetry install` and `poetry check --lock` for current development.
