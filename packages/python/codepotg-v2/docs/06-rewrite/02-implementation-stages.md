# Implementation stages

The stages below build only the approved closed-kernel architecture. Each stage must satisfy its acceptance criteria before dependent stages are marked complete.

## Stage 00 — Governance and package boundaries

Deliverables:

- approved architecture and closed semantic kernel;
- root-first selector and naming contracts;
- template-owned syntax boundary;
- detailed project/pack schemas;
- adapter contracts;
- clean-room policy;
- package task ledgers and progress records.

Acceptance:

- no v2 task asks for old config decoders, old runtime imports, open semantic/facet extension, query selectors, or adapter-rendered source syntax;
- another agent can identify ownership and dependencies without conversation context.

## Stage 01 — Core package foundation

Deliverables:

- isolated package metadata and supported public namespace;
- version/behavior primitives;
- diagnostic, source-span, event, result, and cancellation primitives;
- import-boundary and closed-kernel architecture tests.

Acceptance:

- install and import in a fresh environment;
- no old package imports, global registries, or forbidden dependency direction.

## Stage 02 — Typed document and schema registry

Deliverables:

- location-aware YAML/JSON nodes;
- document family and `apiVersion` registry;
- structural diagnostics;
- schema introspection;
- stable serialization.

Acceptance:

- exact v2 project, pack, and lock dispatch;
- unknown/duplicate fields include spans;
- raw mappings do not escape configuration.

## Stage 03 — Project configuration

Deliverables:

- project name, named semantic sources, executables, security, global commands, and ordered pack instances;
- direct local/Git source, input, scalar output, options, bindings, executable overrides, and per-instance commands;
- immutable typed models.

Acceptance:

- canonical examples decode;
- project-level language, tasks, templateDir, registries/use, and semantic extensions are impossible;
- no compatibility fallback.

## Stage 04 — Pack manifest and file discovery

Deliverables:

- root identity/compatibility, include/exclude, options, bindings, selections, executables, and exact commands;
- one descriptor per included file under `templates/`;
- root-first fixed selectors, generated imports/exports/symbols, and selection folders;
- engine/target inference;
- static/binary copy and partial descriptors;
- authored barrel templates.

Acceptance:

- heterogeneous pack fixtures validate;
- packs cannot add semantic objects/facets/selectors/contexts or syntax-rendering language rules;
- ignored files receive no descriptors;
- no profiles, `filePatterns`, explicit file registry, duplicate descriptors, or special barrel subsystem.

## Stage 05 — Closed semantic kernel and source port

Deliverables:

- provenance and semantic identity;
- structural schemas and schema uses;
- groups, operations, inputs, outputs, failures, effects;
- known HTTP/access/trigger/execution/events facets;
- views, storage mappings, policies, events, listeners, hooks, workflows, and compensation;
- bounded extensions/raw provenance;
- private typed relationship indexes and uniform validation;
- source adapter protocol and conformance.

Acceptance:

- IR imports no source-specific type;
- public contexts are typed rather than generic graph/fact bags;
- adapters cannot extend the kernel;
- in-memory source fixtures validate without filesystem assumptions.

## Stage 06 — Adapter discovery and registries

Deliverables:

- descriptors and API/behavior versions;
- Python entry-point discovery;
- runtime-owned registries;
- configuration/capability validation;
- source, target, engine, provider, ecosystem, writer, cache, and executor conformance suites.

Acceptance:

- official packages can be removed independently;
- duplicate IDs/aliases and incompatible versions fail clearly;
- no global decorator registration;
- no adapter claims semantic extension or emitted syntax ownership.

## Stage 07 — Options, bindings, and generated dependencies

Deliverables:

- typed options/patches only where needed;
- deterministic precedence and provenance;
- pack restrictions;
- external binding catalog and values;
- generated dependency matching by semantic identity/scope/selection/symbol;
- immutable provider/module/path facts;
- unresolved binding readiness.

Acceptance:

- no recursive dictionary merge;
- generated dependencies and external bindings remain distinct;
- templates author all import/export syntax;
- project/path/package/barrel dependencies plan correctly.

## Stage 08 — Selection and artifact planner

Deliverables:

- versioned root-first `.each`/`.all` selector registry;
- nested active-parent selection-folder fan-out;
- stable invocation/artifact identity;
- include, semantic provider, symbol, export, output, command, and contribution graphs;
- semantic and artifact validation;
- deterministic plan inspection/explain;
- semantic-to-artifact impact/blast-radius graph.

Acceptance:

- no render starts on invalid semantic/artifact plan;
- old/reversed/query selectors are rejected;
- cycles, collisions, missing/ambiguous providers, incompatible targets, and unsafe paths are detected;
- every artifact is explainable.

## Stage 09 — Template-engine and target adapter integration

Deliverables:

- immutable documented render context;
- target detection/filename/identifier/path validation per template;
- engine adapter resolution per template;
- include/partial compatibility;
- authored barrels and dependency syntax;
- static/binary staging.

Acceptance:

- one pack renders TypeScript, Dart, YAML, and Markdown files through independent engines/target validators;
- templates own every emitted character;
- cross-target partial misuse and adapter-generated syntax fail conformance.

## Stage 10 — Writers, ownership state, and cache

Deliverables:

- memory, transactional filesystem, and archive writers;
- ownership/generation-state manifest;
- dry run with semantic causes;
- exact comparison;
- writer rollback;
- content-addressed cache.

Acceptance:

- cancellation/failure before commit leaves destination unchanged;
- output state/digests are outside the dependency lock;
- cache changes for every behavior-affecting input.

## Stage 11 — Commands, setup, toolchains, and project manifests

Deliverables:

- security hierarchy and approval records;
- exact opaque commands;
- typed setup/readiness actions;
- Node and Dart project ecosystem adapters;
- known dependency/manifest contributions.

Acceptance:

- server-safe mode denies execution;
- pack command change invalidates approval;
- project contributions remain distinct from application semantics and generated source;
- owned and contributed manifests remain explicit.

## Stage 12 — Initial source, target, and engine packages

Deliverables:

- OpenAPI adapter with typed/versioned `x-codegen` mapping into the closed kernel;
- TypeScript target detection/validation/path adapter;
- Dart target detection/validation/path adapter;
- sandboxed Jinja engine adapter.

Acceptance:

- every package passes shared conformance plus focused tests;
- no package imports core internals;
- source adapter cannot extend semantics;
- target adapters contain no type/literal/import/export/comment/framework renderer.

## Stage 13 — Official packs

Deliverables:

- one modular TypeScript SDK pack;
- one standalone modular Dart SDK pack;
- one Flutter host-application integration pack;
- closed-kernel root-first manifests, templates, static files, barrels, bindings, exact commands, docs, and connected fixtures.

Acceptance:

- no profile/file-ID machinery;
- realistic projects build or validate with declared commands;
- all syntax is template-authored;
- no internal templates/selectors required in project config.

## Stage 14 — Python API and frontends

Deliverables:

- high-level facade;
- sync/async validate, inspect, plan, impact, generate, configure, plugin, pack, cache, and approval operations;
- thin CLI;
- structured MCP-ready operations;
- memory generation examples;
- stable blast-radius data contract.

Acceptance:

- CLI contains no business logic;
- equivalent requests produce equivalent API/CLI/structured plans and impact results.

## Stage 15 — Git distribution and locking

Deliverables:

- local and generic Git pack providers;
- private authentication through existing Git credentials;
- immutable pack cache;
- dependency lock with source/pack/plugin/behavior identities;
- command approval identity tied to exact pack digest.

Acceptance:

- public/private fixtures resolve without stored credentials;
- branch/tag resolves to locked commit;
- drift is visible;
- output hashes remain in ownership state rather than lock.

## Stage 16 — Re-authoring, performance, and release

Deliverables:

- official project examples re-authored to v2;
- old pack requirements studied and new packs authored cleanly;
- connected application-system fixture and impact assertions;
- deterministic full-generation benchmarks;
- conservative incremental generation only after full output equivalence is proven;
- batteries-included/minimal distributions and release checklist.

Acceptance:

- no old code/config decoder dependency;
- no active conflicting resource/model/entity/frontend/UI/open-facet/query-selector/syntax-renderer plans;
- official workflows work from fresh installation;
- docs/tasks match implementation;
- incremental output, when enabled, is byte-for-byte equivalent to full generation.
