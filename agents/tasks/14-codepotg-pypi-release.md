# Task 14 — Publish CodepotG 1.0.0 to PyPI

Status: [~]
Issue: #13
Depends on: Python generator parity and package tests
Commit: pending final local validation
Validation: pending user-run clean build and upload

## Goal

Publish the stable Python/Jinja OpenAPI generator as `codepotg==1.0.0` while preserving compatibility with OpenAPI emitted by CodepotX.

## Package readiness

- [x] Align `pyproject.toml`, `codepotg.__version__`, and CLI version at `1.0.0`.
- [x] Replace deprecated public wording with a stable compatibility-product description.
- [x] Add SPDX license metadata and package-local license file.
- [x] Add PyPI project links, classifiers, keywords, and development dependencies.
- [x] Add source-distribution manifest rules.
- [x] Make the namespaced CLI bootstrap work in both editable checkouts and installed wheels.
- [x] Add `codepotg --version` and `python -m codepotg`.
- [x] Rewrite the package README for PyPI consumers.
- [x] Add guarded release automation that never prints `PUBLISH_TOKEN`.
- [x] Add version and package-metadata tests.
- [x] Add OpenAPI 3.0.3/3.1.0 CodepotX compatibility fixtures.

## Required local validation

- [ ] Install `.[dev]` in a clean virtual environment.
- [ ] Run the full test suite.
- [ ] Run Ruff.
- [ ] Build one sdist and one universal wheel.
- [ ] Pass `twine check`.
- [ ] Verify the wheel contains the legacy runtime modules and bundled templates.
- [ ] Install the wheel in a second clean virtual environment.
- [ ] Run `codepotg --version`, `codepotg --help`, and `python -m codepotg --version`.
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
