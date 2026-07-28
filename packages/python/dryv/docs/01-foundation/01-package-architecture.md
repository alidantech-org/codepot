# Package architecture

## Goal

Dryv is an importable Python runtime with explicit domain boundaries and independently installable interfaces, authoring frontends, and plugins.

## Runtime source layout

```text
src/dryv/
├── __init__.py
├── api/
├── application/
├── config/
├── domain/
│   ├── ir/
│   └── generation/
├── plugins/
├── ports/
├── runtime/
└── infrastructure/
```

The existing `src/dryv/cli/` code is transitional and moves to `dryv-cli`.

## Responsibilities

### `api`

Stable Python-facing requests, results, cancellation, events, runtime facade, and supported exports.

It contains no terminal parsing, target syntax, template-engine implementation, authoring builders, package-manager logic, or concrete project UI.

### `application`

Use cases and coordination:

- load and validate contracts, projects, packs, and plugins;
- inspect plans, artifacts, symbols, state, and compatibility;
- plan and generate;
- emit canonical transport;
- resolve packs through approved providers;
- manage locks, approvals, cache, and ownership state through ports.

Application services depend on domain contracts and ports, not concrete infrastructure.

### `config`

Typed configuration infrastructure:

- safe document decoding;
- project, provider, and pack models;
- typed validation;
- option and binding descriptors;
- schema introspection and serialization.

Raw YAML/JSON values stop here. Configuration cannot add semantic objects, facets, selectors, expressions, or template-context properties.

### `domain.ir`

The closed source-neutral semantic kernel:

```text
contract and groups
semantic identity, names, provenance, tags, and guidance
structural schemas, fields, constraints, and uses
operations, inputs, outputs, failures, effects, and known facets
views, parts, triggers, and flows
storage mappings, fields, keys, indexes, relations, and constraints
policies and access
application events and execution hooks
value sources
workflows, transitions, waits, decisions, branches, and compensation
presentations and view placement
uniform validation and private typed indexes
```

It contains no provider implementation, target syntax, template engine, filesystem, command executor, cache implementation, runtime composition, or interface concern.

### `domain.generation`

Generation semantics:

- pack and file descriptors;
- fixed selector descriptors and contexts;
- template/static invocations;
- stable artifact identity and destinations;
- external bindings;
- generated providers, symbols, imports, and exports;
- target-aware path/module facts;
- dependency, collision, command, and readiness graphs;
- explanation and impact records;
- lifecycle and ownership intent.

It does not render target-language text.

### `plugins`

Public descriptors, API/behavior versions, capabilities, factory loading, runtime registries, and compatibility validation.

Official and third-party plugins use identical public contracts. Plugins cannot extend the semantic kernel or provide target-source renderers.

### `ports`

Interfaces for:

- contract providers/loaders;
- target validation and module/path facts;
- template engines;
- pack providers;
- ecosystem adapters;
- writers;
- cache stores;
- command executors;
- approval stores;
- event sinks.

There is no semantic-extension, facet-registration, selector-registration, or type/literal/import/export renderer port.

### `runtime`

Immutable composition and isolated sessions. Runtime coordinates selected services without global state or plugin mutation of core registries.

The planned `DryvRuntime` facade provides validation, inspection, planning, generation, transport, and state operations.

### `infrastructure`

Concrete implementations for safe YAML/JSON, canonical contract loading, local pack snapshots, memory/archive/filesystem writers, ownership state, entry-point discovery, and future approved caches/providers/executors.

### `dryv-cli`

Separate distribution containing thin argument parsing and terminal presentation only. It creates typed runtime requests, invokes public runtime operations, renders results, and selects exit codes.

## Dependency direction

```text
dryv-cli / IDE / MCP / HTTP / notebook / host application
                         │
                         ▼
                       api
                         │
                         ▼
                    application
                     │        │
                     ▼        ▼
                  domain     ports
                               ▲
                               │
                        infrastructure
```

External package direction:

```text
dryv-cli ----------------------> dryv
dryv-author -------------------> dryv
dryv-template-jinja -----------> dryv
dryv-language-typescript ------> dryv
dryv-language-dart ------------> dryv
```

Rules:

- domain imports no application, infrastructure, runtime, or interface module;
- application imports domain and ports, not concrete infrastructure;
- infrastructure implements ports;
- interfaces import only public runtime APIs;
- plugin packages import only published public contracts;
- plugins never import another plugin's internals;
- only Dryv core defines semantic objects, facets, selectors, and context contracts;
- only pack templates, macros, partials, and static files author generated text;
- `dryv` never depends on `dryv-cli` or `dryv-author`.

## Distribution topology

```text
dryv
dryv-cli
dryv-author
dryv-language-typescript
dryv-language-dart
dryv-template-jinja
```

Reusable packs are independently versioned artifacts and do not need to be hardcoded runtime dependencies.

## Archived package isolation

The archived generator retains its original package and namespace. Dryv does not import or replace its internals and can be tested independently without namespace collisions.

## Architecture tests

The suites verify:

- dependency direction and public/private namespaces;
- no archived implementation imports;
- no interface dependency below the interface layer;
- no plugin-specific imports in the semantic kernel;
- no process-global registries;
- no plugin-defined semantic/facet/selector/context extension path;
- no target-source renderer ports;
- generated text originates only from packs;
- runtime-only and full-family isolated installation.
