# Audit fix handoff — `codepotg-language-typescript`

## Branch

```text
Base: chatgpt/codepotx-restart
Fix branch: chatgpt/codepotx-restart-typescript-audit-fixes
```

Use one slash only. Do not modify `.github/**` or core implementation files.

## Required reading

```text
packages/python/codepotg-language-typescript/docs/audits/2026-07-27-pr-30-audit.md
packages/python/codepotg-language-typescript/docs/tasks/00-package-plan.md
packages/python/codepotg-language-typescript/docs/tasks/PROGRESS.md
packages/python/codepotg-v2/docs/04-plugins/02-language-adapter-contract.md
```

## Required fixes

1. Make direct `TypeScriptTargetOptions(...)` construction as strict as `from_mapping()`.
2. Reject plain strings for enum policy fields.
3. Reject non-string `package_name` with a stable `ValueError`.
4. Reject invalid direct alias collection/item types before sorting or regex operations.
5. Add exact tests proving invalid direct values fail and valid enum values preserve expected suffix/index behavior.
6. Remove version-literal drift by centralizing the semantic plugin version or adding exact metadata/version tests.
7. Make wheel/sdist inspection non-skipping in the release verification path.
8. Run the complete synchronized core and package release commands and append exact evidence to progress.
9. Keep TS-006 and TS-009 blockers explicit. Do not emulate missing planner/symbol/context contracts privately.

## Repair status

- [x] Direct option construction rejects raw strings and other non-enum policy values.
- [x] Non-string package names fail with a stable `ValueError` before regex use.
- [x] Direct alias collection and alias item types are validated before sorting or regex use.
- [x] Adapter construction rejects non-`TypeScriptTargetOptions` values.
- [x] Unit coverage proves rejection behavior and valid extension/index enum behavior.
- [x] Distribution tests build fresh temporary wheel/sdist artifacts and cannot skip because `dist/` is empty.
- [x] Installed distribution and semantic plugin versions are asserted exactly.
- [ ] Exact synchronized Ruff, format, full core/package, release build, and real-wheel checks remain open.
- [ ] TS-006 and TS-009 remain blocked on public core/planner/pack contracts.

## Allowed files

```text
packages/python/codepotg-language-typescript/**
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

cd ../codepotg-language-typescript
python -m pip install -e ../codepotg-v2
python -m pip install -e ".[dev]"
python -m ruff check src tests benchmarks
python -m ruff format --check src tests benchmarks
python -m pytest -vv
python -m build
```

Then install the real core and TypeScript wheels in a fresh environment and run entry-point, identifier, output-path, relative, alias, package, and declaration-suffix checks.

## Completion gate

- invalid direct options are rejected deterministically;
- all existing tests and new tests pass;
- TypeScript compiler oracle passes or an exact environment blocker is recorded;
- wheel/sdist contents are actually inspected after build;
- real-wheel isolated calls pass;
- task/progress statuses are truthful;
- working tree is clean.
