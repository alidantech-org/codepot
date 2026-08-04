# PYTHON-UV-001 — Establish the repository Python workspace

Status: review

Owner: repository / Python packages

## Problem

The Python packages were separate projects with duplicated development extras, package-local source-path injection, README commands that assumed a manually prepared Python environment, package-local guides with editable `pip` installation, generated package metadata checked into source, and distribution tests that directly managed `venv` and `pip`. Internal dependencies such as `dryv` were declared only as published requirements, so local package connection was implicit rather than workspace-governed.

## Scope

- Add one root virtual `uv` project.
- Include every package under `packages/python/` as a workspace member.
- Resolve `dryv` as a workspace dependency during repository development.
- Centralize development tooling in PEP 735 dependency groups.
- Pin the repository development baseline through `.python-version`.
- Remove active-package development-extra duplication and test `pythonpath` injection.
- Replace package README test commands with root-workspace `uv run` commands.
- Convert active-package distribution setup to `uv build`, `uv venv`, and `uv pip`.
- Move remaining package-local environment guides into canonical `.docs` locations and rewrite them around `uv`.
- Remove checked-in generated Python package metadata and ignore future Python build/cache output.
- Document and enforce the workspace workflow for humans and AI agents.
- Include frozen CodepotG for maintenance reproducibility without changing its product status.

## Non-goals

- Replacing setuptools build backends.
- Changing runtime dependency ranges.
- Activating CodepotG development.
- Rewriting frozen CodepotG's internal release tooling.
- Changing package versions or public APIs.
- Modifying `.github/**`, `.archives/**`, `.docs/plan/**`, or `.docs/research/**`.

## Allowed paths

```text
pyproject.toml
.python-version
.gitignore
README.md
AGENTS.md
.docs/project/**
.docs/agents/rules/repository.md
.docs/tasks/cross-cutting/**
.docs/examples/**
.docs/products/dryv/template-jinja/**
packages/python/*/pyproject.toml
packages/python/*/README.md
packages/python/dryv/tests/distribution/**
packages/python/dryv-template-jinja/tests/distribution/**
packages/python/dryv-language-dart/tests/distribution/**
packages/python/dryv-language-typescript/tests/distribution/**
packages/python/dryv-template-jinja/benchmarks/README.md
packages/python/dryv/examples/manual/connected-project/README.md
packages/python/dryv-cli/src/dryv_cli.egg-info/**
uv.lock
```

## Acceptance criteria

- Root `pyproject.toml` is a non-package `uv` workspace.
- All seven Python packages are members.
- `dryv` resolves through `tool.uv.sources` with `workspace = true`.
- One root `.venv` is the documented and enforced environment.
- Root PEP 735 groups own test, lint, typing, and release tooling.
- Active package metadata no longer duplicates repository development extras.
- Package test configuration does not use source-path injection to connect active packages.
- Active distribution tests do not invoke `venv`, `python -m venv`, or `python -m pip`.
- Manual and benchmark workflows use `uv` without environment activation.
- Generated `.egg-info`, Python cache, test cache, and type-checker output are ignored and not tracked as source.
- Root and package READMEs use `uv` commands and do not require activation.
- Python agent rules prohibit manual environment and editable-install workflows.
- A network-enabled `uv lock` and `uv sync --locked --all-packages` succeed before this task moves from review to complete.

## Validation evidence

Completed in the connector environment:

```text
- Audited every packages/python/*/pyproject.toml.
- Verified all members declare Python >=3.11.
- Parsed the proposed root pyproject.toml with Python tomllib.
- Parsed the workspace with uv 0.10.0 up to dependency resolution.
- Confirmed uv recognized the workspace, workspace source, and PEP 735 groups.
- Confirmed uv 0.10.0 supports the selected build, venv, pip, package, all-packages, no-sources, and no-build-isolation options.
- Replaced active-package distribution environment management with uv commands.
- Centralized the connected-project and Jinja benchmark environment guides.
```

Pending because the execution environment has no package-index network access and no populated uv cache:

```bash
uv lock
uv sync --locked --all-packages
uv run --all-packages pytest
uv run ruff check packages/python
```

The task must remain in `review` until those exact commands are run in a network-enabled checkout and their results are recorded.
