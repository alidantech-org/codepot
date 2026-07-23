# Codepot task tracking

This folder is the ordered implementation ledger for the active `codepotx` restart.

## Status

- `[ ]` planned
- `[~]` in progress; an issue must be open
- `[!]` blocked; record the reason and dependency
- `[x]` complete; validation recorded, commit present, and issue closed

## Required task record

Every independently verifiable task records:

```text
Status:
Issue:
Depends on:
Commit:
Validation:
```

Subtasks use checkboxes. A task cannot be marked `[x]` until:

1. all acceptance criteria pass;
2. required compatibility evidence exists;
3. validation commands or equivalent checks are recorded;
4. the implementation commit is on the active branch;
5. the GitHub issue is closed.

## Issue policy

- Open an issue when a planned task is ready to begin.
- Put the issue number in the task file before implementation.
- One issue should represent one reviewable outcome.
- Close the issue immediately after completion and validation.
- Never leave a completed task issue open.
- Close abandoned work with the correct reason and update the task file.

## Ordered files

### Original implementation phases

1. `00-roadmap.md`
2. `01-contract.md`
3. `02-runtime-platform.md`
4. `03-authoring.md`
5. `04-templating.md`
6. `05-generation.md`
7. `06-cli.md`
8. `07-integration-release.md`
9. `08-template-contract.md`
10. `09-generation-hardening.md`
11. `10-site-docs-deploy.md`
12. `11-shipping-validation.md`
13. `12-python-parity-matrix.md`
14. `13-strict-typecheck-recovery.md`
15. `14-codepotg-pypi-release.md`

### CodepotX structure migration

16. `15-codepotx-structure-migration.md` — umbrella program
17. `16-codepotx-architecture-guardrails.md` — baseline and automated boundaries
18. `17-codepotx-contract-restructure.md` — protocol, artifacts, operations, and ports
19. `18-codepotx-authoring-restructure.md` — compiler passes and authoring use cases
20. `19-codepotx-templating-restructure.md` — template compilation, context, variables, and rendering
21. `20-codepotx-generation-restructure.md` — planning, writing, manifests, transactions, commands, and orchestration
22. `21-codepotx-runtime-platform-restructure.md` — typed dispatch and adapter organization
23. `22-codepotx-tests-exports-cleanup.md` — test hierarchy, curated exports, documentation, and cleanup
24. `23-codepotx-structure-integration-gate.md` — final behavioral, type, package, and workspace validation

Do not begin a phase until its dependency gates are met. For the structure migration, read `agents/CODEPOTX_STRUCTURE_GUIDE.md` before opening Task 16.
