# Implementation stages

The stages below build only the new architecture. Each stage must satisfy its acceptance criteria before dependent stages are marked complete.

## Stage 00 — Governance and package boundaries

Deliverables:

- approved architecture and agent rules;
- detailed project and pack schemas;
- plugin contracts;
- clean-room policy;
- package task ledgers and progress records.

Acceptance:

- no v2 task asks for old config decoders or old runtime imports;
- another agent can identify ownership and dependencies without conversation context.

## Stage 01 — Core package foundation

Deliverables:

- `pyproject.toml` and isolated install;
- supported public namespace;
- version primitives;
- diagnostic, source-span, event, result, cancellation primitives;
- import-boundary tests.

Acceptance:

- install and import in a fresh environment;
- architecture tests prove no old package imports and no forbidden dependency direction.

## Stage 02 — Typed document and schema registry

Deliverables:

- location-aware YAML/JSON nodes;
- `(kind, apiVersion)` registry;
- structural diagnostic collection;
- schema introspection;
- stable serialization support.

Acceptance:

- exact v2 project and pack schema dispatch;
- unknown/duplicate fields include source spans;
- raw mappings do not escape the config subsystem.

## Stage 03 — Project configuration

Deliverables:

- metadata, allow, sources, variables, units/toolchains, security, global commands, pack instances;
- output, clean, options, bindings, overrides, pack-instance commands;
- typed immutable models.

Acceptance:

- complete canonical examples decode;
- project-level language/tasks/templateDir are impossible in the typed model;
- no compatibility fallback.

## Stage 04 — Pack manifest and file discovery

Deliverables:

- metadata, compatibility, traits, content, ignore, write policy, options, selections, patterns, files, profiles, dependencies, setup, commands, override policy;
- one file descriptor per discovered source;
- engine/target inference;
- static/binary copy descriptors;
- authored barrel/partial roles.

Acceptance:

- heterogeneous pack fixture validates;
- ignored files never receive descriptors;
- no duplicate descriptor or special barrel subsystem.

## Stage 05 — Neutral IR and source port

Deliverables:

- canonical semantic IR and provenance;
- source adapter protocol and conformance suite;
- immutable source result and digest model.

Acceptance:

- domain IR imports no source-specific type;
- in-memory source fixture works without filesystem assumptions.

## Stage 06 — Plugin discovery and registries

Deliverables:

- plugin descriptors and API versions;
- Python entry-point discovery;
- instance registries;
- configuration ownership and capability validation;
- category conformance harnesses.

Acceptance:

- official plugin packages can be removed independently;
- duplicate IDs/aliases and incompatible versions fail clearly;
- no global decorator registration.

## Stage 07 — Rules, overrides, bindings, imports

Deliverables:

- rule descriptors and typed patches;
- merge policies and provenance;
- pack restrictions;
- binding catalog and project values;
- semantic import/export model;
- unresolved binding readiness.

Acceptance:

- no recursive dictionary merge;
- barrel groups and project-path relative imports plan correctly;
- flexible and strict policies both work.

## Stage 08 — Selection and generation planner

Deliverables:

- once, each, grouped, aggregate, artifact-derived selection;
- folder-pattern fan-out;
- invocation, include, provider, artifact, import, output, command, and contribution graphs;
- complete validation and deterministic plan inspection.

Acceptance:

- no render starts on invalid plan;
- cycles, collisions, missing/ambiguous providers, incompatible targets, and unsafe paths are detected.

## Stage 09 — Template-engine and target adapter integration

Deliverables:

- immutable render context contract;
- target adapter resolution per template;
- engine adapter resolution per template;
- includes/partials compatibility;
- authored barrels;
- named outputs.

Acceptance:

- one pack renders TypeScript, Dart, YAML, and Markdown files through independent adapters;
- cross-target partial misuse fails before render.

## Stage 10 — Writers and cache

Deliverables:

- memory writer;
- transactional filesystem writer;
- archive writer;
- ownership manifest;
- dry run;
- exact comparison;
- rollback;
- content-addressed cache.

Acceptance:

- cancellation/failure before commit leaves destination unchanged;
- cache changes for every behavior-affecting input.

## Stage 11 — Commands, setup, toolchains, and manifests

Deliverables:

- security policy hierarchy;
- approval records;
- structured raw commands;
- typed actions;
- Node and Dart ecosystem adapters;
- dependency/manifest contributions;
- configure question model and readiness actions.

Acceptance:

- server-safe mode denies execution;
- pack command change invalidates approval;
- npm/pnpm/Yarn selection follows project toolchain resolution;
- owned and contributed manifests remain distinct.

## Stage 12 — Initial source, target, and engine packages

Deliverables:

- OpenAPI adapter;
- TypeScript adapter;
- Dart adapter;
- sandboxed Jinja adapter.

Acceptance:

- every package passes shared conformance plus package-specific tests;
- no package imports core internals.

## Stage 13 — Official packs

Deliverables:

- TypeScript SDK;
- Dart SDK;
- Flutter SDK;
- authored manifests, templates, static files, barrels, bindings, setup, commands, docs, and fixtures.

Acceptance:

- modular and monolithic profiles where applicable;
- realistic projects build or validate with declared toolchains;
- no internal details required in project config.

## Stage 14 — Python API frontends

Deliverables:

- high-level facade;
- sync/async operations;
- configure workflow;
- thin CLI;
- structured MCP-ready operations;
- memory generation examples.

Acceptance:

- CLI contains no business logic;
- same request produces equivalent API/CLI/MCP-structured result.

## Stage 15 — Git distribution and locking

Deliverables:

- local, Git, and GitHub shorthand providers;
- private repository authentication through existing Git credentials;
- pack cache;
- immutable lock file;
- command approval identity tied to pack digest.

Acceptance:

- public/private pack fixtures resolve without storing credentials;
- branch/tag resolves to locked commit;
- drift is visible.

## Stage 16 — Re-authoring and release

Deliverables:

- official project examples rewritten to v2;
- old pack behavior studied and new packs authored cleanly;
- parity/difference reports;
- batteries-included and minimal distribution packaging;
- release checklist.

Acceptance:

- no old code/config decoder dependency introduced;
- official workflows work from fresh installation with default plugins;
- docs and tasks match implementation.
