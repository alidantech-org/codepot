# Parallel agent working rules

These rules exist so several agents can implement CodepotG v2 in separate conversations without changing the architecture or duplicating work.

## Mandatory reading order

Before editing code, every agent must read:

1. `docs/00-governance/00-approved-architecture.md`;
2. the design document for the assigned area;
3. `docs/tasks/PARALLEL_WORK.md`;
4. the assigned package's `docs/tasks/README.md` and task files;
5. the latest `PROGRESS.md` entries.

## Prohibited work

Agents must not:

- copy modules from `packages/python/codepotg` into v2;
- import v1 internals;
- add a v1 `tasks` configuration decoder;
- add a `paths.yaml` decoder or runtime fallback;
- add project-level `language` or pack-level single-language assumptions;
- add system-generated barrels without an authored template;
- treat static pack files as opt-in emissions;
- add raw dictionary deep-merging for rules or overrides;
- put generation logic in the CLI;
- create global decorator registries;
- execute shell commands from templates;
- create, modify, or depend on `.github` automation;
- create a new branch without explicit user instruction.

The old package remains available for old projects. V2 is a clean replacement, not a compatibility wrapper.

## Task ownership

Before beginning a task, add or update its entry in `docs/tasks/PARALLEL_WORK.md` with:

- task ID;
- assigned package or subsystem;
- status `claimed`;
- agent/chat identifier when available;
- expected files;
- declared dependencies.

One task may have one active owner. Another agent may work on a different task only when file ownership does not overlap.

## Task states

Use exactly these states:

- `planned` — documented but not claimed;
- `claimed` — assigned and not yet started;
- `in_progress` — implementation has begun;
- `blocked` — cannot proceed until a named dependency is resolved;
- `review` — implementation complete and awaiting verification;
- `complete` — acceptance criteria and required tests passed;
- `superseded` — replaced by a documented decision.

Checkboxes indicate completion only:

```text
- [ ] not complete
- [x] complete
```

Do not mark a task complete merely because files were created.

## Progress records

Every coherent commit must add a row to the owning package's `docs/tasks/PROGRESS.md` containing:

- date;
- commit SHA;
- task ID;
- status;
- tests run and results;
- design decisions or deviations;
- blockers and next task.

Do not rewrite old progress rows. Append corrections as new rows.

## Architecture changes

An agent may not silently change an approved contract.

A proposed change must:

1. describe the problem;
2. identify affected documents and packages;
3. show why the current contract cannot support the requirement;
4. define compatibility and security consequences;
5. be approved before implementation;
6. update the governance document and affected tasks first.

## Commit boundaries

Prefer one coherent concern per commit. Examples:

- typed diagnostic primitives;
- project configuration model;
- TypeScript identifier policy;
- Jinja include resolver;
- transactional staging writer.

Do not combine unrelated adapters or broad refactors in one commit.

## Tests

- Unit tests cover one rule, class, or function where practical.
- Contract tests are reusable for all implementations of a port.
- Integration tests are small vertical slices.
- Fixtures must be inspectable and use realistic names and output.
- Tests must not require network access, global environment mutation, or order dependence.
- A package task is complete only when its listed acceptance tests pass.

## Documentation truth

When code and documentation disagree, the approved design document wins until an approved architecture change updates it.

Implementation discoveries must be documented immediately so another agent does not repeat the investigation or make an incompatible assumption.
