# Python workspace

All Python packages under `packages/python/` are managed as one `uv` workspace from the repository root.

## Why this is the canonical workflow

The workspace provides:

- one automatically managed root `.venv`;
- one dependency resolution and `uv.lock` for the whole Python package family;
- editable installation of workspace members;
- explicit resolution of `dryv` from the local workspace instead of PyPI;
- package-specific commands from any repository directory;
- standardized PEP 735 development dependency groups;
- no manual virtual-environment creation or activation.

The root project is virtual (`tool.uv.package = false`): it exists only to coordinate development and is never built or published.

## Workspace members

```text
packages/python/codepotg
packages/python/dryv
packages/python/dryv-author
packages/python/dryv-cli
packages/python/dryv-language-dart
packages/python/dryv-language-typescript
packages/python/dryv-template-jinja
```

CodepotG remains frozen. Workspace membership allows reproducible maintenance and testing; it does not make CodepotG an active product or a dependency of Dryv.

## First setup

Install `uv`, then run from the repository root:

```bash
uv sync --all-packages
```

`uv` selects the Python version declared in `.python-version`, creates or updates the root `.venv`, resolves the workspace, and installs all members in editable mode. Do not create or activate a package-local virtual environment.

## Common commands

Run the complete Python test suite:

```bash
uv run --all-packages pytest
```

Run one package's tests while retaining the connected workspace and root development tools:

```bash
uv run --all-packages pytest packages/python/dryv/tests
uv run --all-packages pytest packages/python/dryv-author/tests
uv run --all-packages pytest packages/python/dryv-cli/tests
```

Lint all Python packages:

```bash
uv run ruff check packages/python
```

Run authoring type checks:

```bash
uv run --all-packages mypy packages/python/dryv-author/src
uv run --all-packages pyright packages/python/dryv-author
```

Run a package-provided command:

```bash
uv run --package dryv-cli dryv --help
```

Build a publishable package without workspace source overrides:

```bash
uv build --package dryv --no-sources
```

## Dependency changes

Runtime dependencies remain in the owning package's `[project].dependencies`:

```bash
uv add --package dryv '<dependency>'
```

Repository-only tools belong in a root dependency group:

```bash
uv add --group test '<test-tool>'
uv add --group lint '<lint-tool>'
uv add --group typing '<typing-tool>'
uv add --group release '<release-tool>'
```

After dependency metadata changes:

```bash
uv lock
uv sync --locked --all-packages
```

Commit `pyproject.toml`, affected member `pyproject.toml` files, and `uv.lock` together.

## Distribution isolation

Active-package distribution tests must also use `uv`:

```text
uv build
uv venv
uv pip install --python <isolated-python>
```

This keeps isolated wheel checks explicit without reintroducing `venv`, `virtualenv`, or direct `pip` management.

## Prohibited workflows

Do not use these for repository development or active-package test setup:

```text
python -m venv ...
virtualenv ...
source .venv/bin/activate
.venv\Scripts\activate
pip install -e ...
python -m pip install ...
```

Do not add package-local `.venv` directories, independently maintained requirements files, or source-path injection to connect workspace packages. Use `uv run`, `uv sync`, workspace sources, and declared dependency groups instead.
