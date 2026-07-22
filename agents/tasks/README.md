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

1. `00-roadmap.md`
2. `01-contract.md`
3. `02-runtime-platform.md`
4. `03-authoring.md`
5. `04-templating.md`
6. `05-generation.md`
7. `06-cli.md`
8. `07-integration-release.md`

Do not begin a phase until the dependency gates in the roadmap are met.
