# Task 14 — Prepare CodepotG 1.0.0 for PyPI

Status: [~]
Issue: #13
Depends on: Python generator parity and package tests
Validated code: `ebbc8f0`
Validation: `python scripts/release.py check` passed on Windows with Python 3.12 on 2026-07-23

## Goal

Prepare the stable Python/Jinja OpenAPI generator as `codepotg==1.0.0` while preserving compatibility with OpenAPI emitted by CodepotX.

The local release gate has passed. PyPI upload and installation from PyPI remain intentionally pending.

## Public configuration contract

- [x] Use `Codepotg.yaml` as the only automatically discovered Python generator config.
- [x] Reject `CodepotFile.yml` and `CodepotFile.yaml` with a migration message because those names belong to the TypeScript workflow.
- [x] Allow another explicit non-legacy YAML path through `--config`.
- [x] Make `templateDir` / `templates` optional.
- [x] Use the bundled template pack selected by `language` when no custom path is configured.
- [x] Remove implicit working-directory template discovery.
- [x] Make `codepotg init --yes` create `Codepotg.yaml` without a fake local template path.
- [x] Update generate, init, task-add, runtime messages, README, release guide, and changelog.
- [x] Add installed-wheel smoke coverage for config creation and bundled-template generation.

## Reported test failure audit

The user initially ran 210 tests before this migration: 185 passed and 25 failed.

- [x] Fix the real eager `codepotg --version` CLI bug.
- [x] Fix bundled-template resolution for the retired source path shape.
- [x] Correct the stale naming-contract assertion.
- [x] Replace the deleted package-root `openapi.yaml` fixture with a committed self-contained fixture.
- [x] Point shared tests at bundled templates under `src/codepotg/templates`.
- [x] Migrate config loader, workflow, and CLI tests to `Codepotg.yaml`.
- [x] Preserve command, cleanup, defaults, lifecycle, inference, and rendering coverage.
- [x] Rerun all tests and classify remaining failures: 213 passed after fixing the debug fixture pack.

## Package readiness

- [x] Align `pyproject.toml`, `codepotg.__version__`, and CLI version at `1.0.0`.
- [x] Describe CodepotG as the supported OpenAPI compatibility generator.
- [x] Add SPDX license metadata and package-local license file.
- [x] Add PyPI project links, classifiers, keywords, and development dependencies.
- [x] Add source-distribution manifest rules, including YAML fixtures.
- [x] Make the namespaced CLI bootstrap work in editable checkouts and installed wheels.
- [x] Add `codepotg --version` and `python -m codepotg`.
- [x] Add a PyPI consumer README and release guide.
- [x] Add guarded release automation that never prints `PUBLISH_TOKEN`.
- [x] Add version and package-metadata tests.
- [x] Add OpenAPI 3.0.3/3.1.0 CodepotX compatibility fixtures.

## Required local validation

- [ ] Install `.[dev]` in a separate clean development virtual environment.
- [x] Run the full test suite: 213 passed.
- [x] Run Ruff.
- [x] Create `Codepotg.yaml` through the installed CLI.
- [x] Run bundled TypeScript generation from the installed wheel in dry-run mode.
- [x] Build one sdist and one universal wheel.
- [x] Pass `twine check`.
- [x] Verify the wheel contains runtime modules and bundled templates.
- [x] Install the wheel in a second clean virtual environment.
- [x] Run `codepotg --version`, `codepotg --help`, and `python -m codepotg --version`.
- [ ] Upload `codepotg==1.0.0` using the local ignored `PUBLISH_TOKEN`.
- [ ] Install `codepotg==1.0.0` from PyPI and rerun the smoke test.

## Post-release CodepotX gate

- [ ] Emit OpenAPI 3.0.3 or 3.1.0 from CodepotX.
- [ ] Load it through CodepotG.
- [ ] Run at least the debug template pack in dry-run mode.
- [ ] Run one production template pack.
- [ ] Record unsupported extension or schema differences as CodepotX projection fixes.

## Completion

Close issue #13 only after the exact uploaded artifacts and PyPI installation have been validated.
