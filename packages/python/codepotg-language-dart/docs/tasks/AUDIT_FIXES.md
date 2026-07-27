# Audit fix handoff — `codepotg-language-dart`

## Branch

```text
Base: chatgpt/codepotx-restart
Fix branch: chatgpt/codepotx-restart-dart-audit-fixes
```

Use one slash only. Do not modify `.github/**` or core implementation files.

## Required reading

```text
packages/python/codepotg-language-dart/docs/audits/2026-07-27-pr-30-audit.md
packages/python/codepotg-language-dart/docs/tasks/00-package-plan.md
packages/python/codepotg-language-dart/docs/tasks/PROGRESS.md
packages/python/codepotg-v2/docs/04-plugins/02-language-adapter-contract.md
```

## Required fixes

1. Make direct `DartTargetOptions(...)` construction as strict as `from_mapping()`.
2. Reject plain strings for enum policy fields.
3. Reject non-string `package_name` with a stable `ValueError`.
4. Add exact tests proving invalid direct values fail and valid enum values preserve privacy/keyword behavior.
5. Centralize the semantic plugin version or add exact installed-metadata/version tests.
6. Make wheel/sdist inspection non-skipping in the release verification path.
7. Run representative identifier and URI fixtures against a real Dart SDK.
8. Run the complete synchronized core and package release commands and append exact evidence.
9. Keep DART-006 and DART-009 blockers explicit; do not invent missing planner/symbol/context contracts.

## Allowed files

```text
packages/python/codepotg-language-dart/**
packages/python/codepotg-v2/docs/tasks/PARALLEL_WORK.md
```

## Required verification

```bash
cd packages/python/codepotg-v2
python -m pip install -e ".[dev]"
python -m ruff check src tests
python -m ruff format --check src tests
python -m pytest -vv
python -m build

cd ../codepotg-language-dart
python -m pip install -e ../codepotg-v2
python -m pip install -e ".[dev]"
python -m ruff check src tests benchmarks
python -m ruff format --check src tests benchmarks
python -m pytest -vv
python -m build
```

Then install the real core and Dart wheels in a fresh environment and run entry-point, identifier, output-path, relative URI, package URI, and explicit URI checks.

## Completion gate

- invalid direct options are rejected deterministically;
- all existing and added tests pass;
- real Dart SDK oracle passes;
- wheel/sdist contents are actually inspected after build;
- real-wheel isolated calls pass;
- task/progress statuses are truthful;
- working tree is clean.
