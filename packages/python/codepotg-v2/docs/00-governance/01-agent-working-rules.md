# Parallel agent working rules

These rules allow several agents to implement CodepotG v2 without changing the architecture or duplicating work.

## Mandatory reading order

Before editing implementation code, every agent must read:

1. `docs/00-governance/00-approved-architecture.md`;
2. `docs/00-governance/04-closed-semantic-kernel.md`;
3. the detailed design document for the assigned area;
4. `docs/tasks/PARALLEL_WORK.md`;
5. the assigned package task files;
6. the latest `PROGRESS.md` entries.

## Prohibited work

Agents must not:

- copy modules from `packages/python/codepotg` into v2 or import old internals;
- add a v1 `tasks` or `paths.yaml` decoder/fallback;
- add project-level `language`, registries/use, hidden pack profiles, `filePatterns`, or ordinary-file registries;
- add neutral `resource`, `model`, `entity`, `frontend`, or `ui` semantic/selector/context roots;
- add class/interface/type/struct/record as schema kinds;
- add reversed selector roots such as `http.groups` or `events.operations`;
- add arbitrary selector query/traversal DSLs;
- let adapters, plugins, packs, or templates register semantic objects, relationships, facets, selectors, expression roots, context properties, or semantic validators;
- expose generic node/edge/fact bags as the public IR/template API;
- add semantic `fileName`, `filePath`, `directory`, or language naming conveniences;
- let language adapters render types, literals, comments, imports, exports, validators, decorators, formatting, or framework syntax;
- generate barrels/imports/exports without authored templates/macros;
- treat static pack files as opt-in emissions;
- deep-merge raw dictionaries for options/overrides;
- put generation logic in CLI;
- create process-global decorator registries;
- let templates access filesystem/network/environment/commands or write files;
- store generated output hashes in `codepotg.lock.yaml`;
- start incremental generation before deterministic full generation and impact analysis are proven;
- create, modify, or depend on `.github` automation;
- create a new branch without explicit user instruction;
- push anywhere except the user-approved branch.

The old package remains available for old projects. V2 is a clean replacement, not a compatibility wrapper.

## Fixed conventions

Agents must preserve:

```text
x.name.{casing}.{number}
```

and outer-to-inner paths such as:

```text
group.operations
operation.inputs
operation.facets.http
workflow.steps
step.compensation.operation
```

Ordinary generation uses root-first selectors such as `groups.operations.each`, `groups.storage.mappings.each`, and `groups.views.each`.

Templates, macros, partials, and static files own every emitted character.

## Task ownership

Before beginning an implementation task, add/update its entry in `docs/tasks/PARALLEL_WORK.md` with:

- task ID;
- package/subsystem;
- status `claimed`;
- agent/chat identifier when available;
- expected files;
- declared dependencies.

One task has one active owner. Another agent may work on a different task only when file ownership does not overlap.

Documentation synchronization requested explicitly by the user may span affected package docs/tasks without claiming implementation files; it must still be recorded in progress evidence.

## Task states

Use exactly:

- `planned`;
- `claimed`;
- `in_progress`;
- `blocked`;
- `review`;
- `complete`;
- `superseded`.

Checkboxes indicate completion only. Do not mark work complete merely because files were created.

## Progress records

Every coherent implementation commit adds a row to the owning package's `docs/tasks/PROGRESS.md` containing:

- date;
- commit SHA/range;
- task ID;
- status;
- exact tests/evidence;
- design decisions/deviations;
- blockers/next task.

Documentation-only architecture alignment records exact inspected paths and explicitly state that runtime tests were not run. Do not rewrite old progress rows; append corrections.

## Architecture changes

An agent may not silently change an approved contract.

A proposal must:

1. describe the proven problem/use cases;
2. identify affected kernel classification and packages;
3. show why current concepts cannot represent it;
4. define public IR/context/selector/configuration impact;
5. define compatibility, security, determinism, lock/cache/impact consequences;
6. receive explicit approval;
7. update governance, detailed docs, examples, tasks, conformance, and behavior versions before implementation.

Adding a plugin/facet/key without this process is prohibited.

## Commit boundaries

Prefer one coherent concern per commit, for example:

- diagnostic/version primitives;
- schema/group/operation kernel types;
- known access facet;
- root-first selector registry;
- TypeScript module-path validation;
- Jinja include resolver;
- transactional writer.

Do not mix unrelated implementation lanes.

## Tests

- Unit tests cover focused behavior.
- Contract/conformance tests are reusable for every implementation of a port.
- Architecture tests enforce closed-kernel and template-owned syntax boundaries.
- Integration tests are small inspectable vertical slices.
- Fixtures use realistic connected semantics and output.
- Tests do not require uncontrolled network, global environment mutation, or order dependence.
- A package task is complete only when its acceptance tests pass.

## Documentation truth

When code and documentation disagree, the governing approved architecture and closed-kernel documents win until an approved change updates them.

Implementation discoveries are documented immediately so another agent does not repeat the investigation or make an incompatible assumption.
