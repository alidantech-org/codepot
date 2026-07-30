# Dryv implementation stages

Each stage preserves the closed-kernel architecture and must satisfy its acceptance criteria before dependent work is considered complete.

## Stage 0 — Package rebrand and isolation

Deliverables:

- `dryv`, `dryv-author`, `dryv-template-jinja`, `dryv-language-typescript`, and `dryv-language-dart` distributions;
- renamed import namespaces, entry points, manifests, project files, API versions, and ownership state;
- removed retired source package;
- archived generator left untouched.

Acceptance:

- no old names or removed-package references in the Dryv family;
- all packages install together without namespace collisions;
- complete lint, tests, build, wheel, and connected-project verification.

## Stage 1 — Runtime package boundary

Deliverables:

- canonical IR, diagnostics, configuration, plugin contracts, planning, generation coordination, and managed output in `dryv`;
- public `DryvRuntime` facade;
- no terminal parsing or UI presentation inside the runtime distribution.

Acceptance:

- runtime-only installation supports validation, planning, memory output, archive output, and managed writes;
- `dryv` does not depend on `dryv-cli` or `dryv-author`.

## Stage 2 — Standalone CLI

Deliverables:

- `dryv-cli` distribution and `dryv_cli` namespace;
- `dryv` executable;
- validate, inspect, plan, generate, IR emission, plugin, and state commands.

Acceptance:

- command handlers call only public runtime operations;
- uninstalling the CLI removes no runtime capability;
- structured API and CLI requests produce equivalent results.

## Stage 3 — Contract providers

Deliverables:

- public contract-provider contract;
- canonical IR file provider;
- Python module/callable provider;
- host-supplied in-memory contract support;
- provider validation, provenance, cancellation, and diagnostics.

Acceptance:

- `dryv-author` can feed the runtime without writing an intermediate transport file;
- every provider result is validated as a public immutable `Contract`;
- provider-specific objects never enter planning or templates.

## Stage 4 — Canonical IR and transport

Deliverables:

- closed typed semantic kernel;
- stable identities, names, refs, validation, tags, guidance, value sources, presentations, and known relationships;
- deterministic strict JSON/YAML transport;
- runtime-owned codec and digest.

Acceptance:

- all supported fixtures round-trip exactly;
- unsupported versions and unknown fields fail safely;
- authoring builders, Pydantic models, providers, target plugins, and runtime services never appear in transport.

## Stage 5 — Project and pack configuration

Deliverables:

- typed `dryv.yaml` and `DryvPack.yaml` contracts;
- contract-provider configuration;
- local/Git pack locators;
- options, bindings, selectors, symbols, imports, exports, commands, and security declarations;
- introspection for CLI, IDE, and cookbook tooling.

Acceptance:

- raw mappings do not escape the configuration layer;
- unknown fields, duplicates, unsafe paths, invalid refs, and unsupported commands fail before generation;
- current examples decode into immutable models.

## Stage 6 — Plugin system

Deliverables:

- public descriptors, versions, capabilities, factories, and conformance helpers;
- entry-point discovery and session-owned registries;
- target, template-engine, provider, pack-provider, ecosystem, writer, cache, and executor ports where justified.

Acceptance:

- official and third-party plugins use the same contracts;
- no plugin extends semantic objects, facets, selectors, expressions, or context roots;
- no target plugin renders source syntax;
- duplicate or incompatible plugins fail with stable diagnostics.

## Stage 7 — Pack discovery and planning

Deliverables:

- deterministic local pack discovery;
- fixed selectors and selection-folder expansion;
- stable artifact identities and destinations;
- target/engine inference;
- generated providers, symbols, imports, exports, and module/path facts;
- complete collision and safety checks;
- plan explanation and impact edges.

Acceptance:

- no renderer or writer is called for an invalid plan;
- every artifact has a stable semantic and template cause;
- templates own all emitted text.

## Stage 8 — Rendering and target plugins

Deliverables:

- bounded immutable prepared contexts;
- sandboxed Jinja engine;
- TypeScript and Dart target validation and path facts;
- declared partials, static files, binary files, and authored barrels.

Acceptance:

- one contract drives valid TypeScript and Dart projects;
- generated projects pass real compiler/analyzer checks;
- engine and target plugins have no semantic or output ownership outside their contracts.

## Stage 9 — Writers and ownership state

Deliverables:

- memory output;
- deterministic archives;
- transactional managed filesystem output;
- `.dryv/generation-state.json`;
- create/change/delete/leave/protect reporting;
- stale-file cleanup and manual-edit protection.

Acceptance:

- failure or cancellation before commit leaves destination and state unchanged;
- generated hashes stay outside `dryv.lock.yaml`;
- fault-injection and Windows file-lock scenarios pass.

## Stage 10 — Git packs and trust

Deliverables:

- local and generic Git providers;
- immutable resolved commits and snapshots;
- credential separation and redaction;
- safe cache and `dryv.lock.yaml`;
- command approvals tied to exact pack identity.

Acceptance:

- public and private packs resolve without stored credentials;
- mutable refs become exact locked commits;
- frozen/offline integrity checks are deterministic.

## Stage 11 — Commands and ecosystem integration

Deliverables:

- exact command plans, provenance, approvals, host policy, environment restrictions, timeouts, cancellation, and cleanup;
- typed Node, Dart, and future ecosystem contribution plans.

Acceptance:

- server-safe mode denies execution;
- no shell interpolation or package-manager inference;
- command and manifest work never expands application semantics.

## Stage 12 — Explain, impact, and incremental generation

Deliverables:

- semantic-to-selection and selection-to-artifact edges;
- generated-provider, template, partial, pack, config, and command causes;
- serializable blast-radius results;
- conservative incremental generation.

Acceptance:

- incremental output is byte-for-byte equal to a fresh complete generation;
- broader safe regeneration is used whenever exact impact cannot be proven.

## Stage 13 — Packs and connected system fixtures

Deliverables:

- reusable TypeScript, Dart, Flutter, backend, workflow, event, storage, and documentation packs;
- one realistic application-system contract;
- exact dependency and impact assertions.

Acceptance:

- all target syntax is template-authored;
- pack dependencies resolve through semantic identity and declared symbols;
- realistic outputs compile, analyze, or otherwise validate.

## Stage 14 — Cookbook and release

Deliverables:

- executable Dryv Cookbook;
- public API and CLI references;
- plugin and pack authoring guides;
- security and reproducibility guidance;
- release matrix and isolated-wheel evidence.

Acceptance:

- docs and examples match code;
- every recipe runs against published packages;
- no archived dependency or conflicting architecture remains;
- complete generation is proven before incremental mode is enabled.
