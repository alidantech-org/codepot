# Task 09 — Build the Project Feature for `dryv.yaml`

Status: [ ]
Owner: `packages/python/dryv`
Depends on: Task 08
Validation: project-config tests, architecture tests

## Goal

Create `features/project` as the sole owner of the meaning and validation of `dryv.yaml` inside Dryv Engine.

`dryv.yaml` is usage configuration. It connects canonical IR or an Author Backend with packs, project bindings, resource identities, generation options and artifact destinations. It must not redefine software semantics.

## Project configuration must be able to describe

- source of Canonical IR: supplied IR resource or Author Backend request;
- active packs and pack instances;
- pack options;
- project-specific bindings;
- logical output roots/destinations;
- render capability requirements or preferred render sessions where usage needs them;
- cache mode (`use`, `refresh`, `off`);
- build mode such as normal render, dry-run/plan, artifact stream;
- resource identifiers needed by the build;
- explicit configuration version.

The exact user-facing syntax must follow the approved current `dryv.yaml` contract. Do not invent new field names merely to satisfy this task; migrate existing approved fields and add only the fields required by already-approved architecture decisions.

## Resource boundary

The Project Feature consumes logical resource references/contents supplied to Runtime. It must not open arbitrary user paths or run Git commands. The Project Client is responsible for collecting local/private resources.

## Validation

Validate:

- version compatibility;
- required IR/author source exclusivity;
- duplicate pack identities;
- invalid cache/build modes;
- invalid or unsafe logical output destinations;
- missing required project bindings where determinable at project-config stage;
- deterministic normalized project configuration.

## Non-goals

- Do not load pack contents here.
- Do not acquire files from the user's filesystem.
- Do not call render/author sessions.
- Do not plan artifacts.

## Allowed paths

- `packages/python/dryv/src/dryv/features/project/**`
- existing `dryv/config/**` modules being migrated
- corresponding tests/docs

## Acceptance criteria

- Runtime consumes `dryv.yaml` through Project Feature only.
- project configuration is normalized deterministically.
- no filesystem/network/server behavior exists in the Feature.
- current supported configuration behavior is either preserved or explicitly migrated with tests/docs.

## Validation

Add fixture tests for minimal IR-source config, author-source config, multiple packs, options/bindings, cache/build modes and invalid conflicts. Run architecture tests and `git diff --check`.
