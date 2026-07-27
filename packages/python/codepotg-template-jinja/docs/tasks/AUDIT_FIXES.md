# Audit fix handoff — `codepotg-template-jinja`

Use this file as the scoped handoff for the next fixing agent.

## Branch

```text
Base: chatgpt/codepotx-restart
Fix branch: chatgpt/codepotx-restart-jinja-audit-fixes
```

Use only one slash. Do not create another branch and do not modify `.github/**`.

## Required reading

```text
packages/python/codepotg-template-jinja/docs/audits/2026-07-27-pr-28-audit.md
packages/python/codepotg-template-jinja/docs/ENGINE_CONTRACT.md
packages/python/codepotg-template-jinja/docs/tasks/00-package-plan.md
packages/python/codepotg-template-jinja/docs/tasks/PROGRESS.md
packages/python/codepotg-v2/docs/00-governance/00-approved-architecture.md
packages/python/codepotg-v2/docs/04-plugins/03-template-engine-adapter-contract.md
```

## Required work

1. Run every exact core and Jinja release command against the synchronized real repository checkout.
2. Run Ruff check and format check.
3. Build the real core and Jinja wheel/sdist artifacts.
4. Install both real wheels into a new environment and repeat entry-point, simple render, and static-partial render checks.
5. Record exact command output in `docs/tasks/PROGRESS.md`.
6. Keep JINJA-008 blocked and do not invent named-output contracts.
7. Add a documented/tested decision for `loop.cycle()` and `loop.changed()`:
   - keep denied and document them; or
   - safely whitelist only the exact audited `LoopContext` callables.
8. Correct root non-string source diagnostics so root failures do not use the partial-only family.
9. Do not add filesystem loaders, pack-provider access, target rendering, writing, commands, or private core imports.

## Files normally allowed

```text
packages/python/codepotg-template-jinja/**
packages/python/codepotg-v2/docs/tasks/PARALLEL_WORK.md
```

Do not modify core implementation files.

## Completion gate

The fix is complete only when:

- all existing 150 tests still pass;
- any added compatibility/diagnostic tests pass;
- Ruff and formatting pass;
- real core suite passes;
- wheel/sdist build passes;
- real-wheel isolated discovery/render passes;
- `git status --short` is empty;
- task/progress status is truthful and includes exact evidence.
