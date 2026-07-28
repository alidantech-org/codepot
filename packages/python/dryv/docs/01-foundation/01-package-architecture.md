# Package architecture

## Goal

Dryv is a clean, importable Python application with explicit domain boundaries and independently installable adapters/infrastructure packages.

The implementation directory is `packages/python/dryv`; the eventual supported Python namespace is `dryv`.

## Core source layout

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
├── infrastructure/
└── cli/
```

## Responsibilities

### `api`

Stable Python-facing requests, results, runtime events, sessions, application facade, and supported exports.

It contains no filesystem, CLI, OpenAPI, Jinja, TypeScript, Dart, package-manager, or target-source implementation.

### `application`

Use cases and orchestration:

- configure;
- validate;
- inspect;
- compile/serialize generation plans;
- explain artifacts and symbols;
- query impact/blast radius;
- generate;
- resolve packs;
- manage approvals/locks/cache/generation state;
- inspect plugins and readiness.

Application services depend on domain types and ports, not concrete infrastructure.

### `config`

Typed configuration infrastructure:

- location-aware document nodes;
- document/schema registry;
- project and pack models;
- typed decoding/validation;
- typed option/patch descriptors;
- schema introspection and serialization.

Raw YAML/JSON values stop here. Configuration cannot add semantic kernel objects, facets, selectors, expression roots, or template-context properties.

### `domain.ir`

The closed source-neutral semantic kernel:

```text
contract/groups
semantic identity and provenance
semantic names
structural schemas, fields, constraints, and schema uses
operations: inputs, outputs, failures, effects
known HTTP/access/trigger/execution/events facets
views, parts, triggers, and flows
storage mappings, fields, keys, indexes, relations, constraints
policies and declared/effective access
application events, listeners, and execution hooks
workflows, steps, transitions, waits, decisions, branches, compensation
bounded raw/extensions
uniform semantic validation
private typed relationship indexes
```

It does not contain neutral resources, models, entities, frontends, UI roots, generated classes/interfaces/types, target syntax, or arbitrary plugin-defined facts.

It must not import OpenAPI, template engines, target adapters, filesystems, commands, caches, runtime composition, or CLI concerns.

The internal representation may use typed graph indexes. The public domain/template contracts remain explicit typed objects.

### `domain.generation`

Generation semantics:

- pack/file descriptors;
- root-first fixed selector descriptors/instances;
- selection folders and active outer-to-inner contexts;
- template/static invocations;
- stable artifact identity and destinations;
- external bindings;
- generated provider/symbol/import/export relationships;
- target-aware path/module facts;
- include/dependency/collision/command graphs;
- explain/provenance records;
- semantic-to-artifact impact graph;
- readiness, lifecycle, ownership, and generation-state intent.

It does not render target-language source text.

### `plugins`

Public adapter/infrastructure descriptors, API/behavior versions, capabilities, entry-point discovery, runtime-owned registries, and compatibility validation.

Official packages use the same APIs as third parties. The plugin system cannot extend application semantics or provide target source renderers.

### `ports`

Interfaces implemented by adapters/infrastructure:

- source adapter that normalizes into the closed kernel;
- target/language detection, validation, and module/path adapter;
- template-engine adapter;
- pack provider;
- ecosystem/toolchain adapter;
- artifact writer;
- cache store;
- command executor;
- approval store;
- event sink.

There is no semantic facet/selector plugin port and no type/literal/import/export renderer port.

### `runtime`

Immutable composition and isolated sessions. Runtime coordinates selected services without process-global state or permitting adapters to mutate kernel registries.

### `infrastructure`

Concrete implementations for:

- safe YAML/JSON parsing;
- local and generic Git pack snapshots;
- filesystem, memory, and archive writers;
- ownership/generation-state persistence;
- content-addressed cache;
- subprocess execution;
- dependency locks;
- approval persistence;
- Python entry-point discovery.

### `cli`

Thin argument parsing and terminal presentation only. It constructs typed API requests, invokes application services, renders results, and selects exit codes.

## Dependency direction

```text
CLI / Python facade / MCP / HTTP / IDE
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

Rules:

- domain imports no application, infrastructure, runtime, or CLI module;
- application imports domain and ports, not concrete infrastructure;
- infrastructure implements ports and may import public domain/config contracts;
- CLI/frontends import only public API/presentation helpers;
- adapter packages import only published public contracts;
- adapters never import another adapter's internals;
- only core/domain defines semantic objects/facets/selectors/context contracts;
- only authored pack files produce generated text.

## Distribution topology

Planned distributions:

```text
dryv
dryv
dryv-openapi
dryv-language-typescript
dryv-language-dart
dryv-template-jinja
dryv-pack-typescript-sdk
dryv-pack-dart-sdk
dryv-pack-flutter-sdk
```

`dryv` is minimal. `dryv` is the batteries-included distribution installing compatible official defaults.

## Namespace transition rule

V2 is developed/tested separately from the old package. It must not rely on side-by-side installation of two distributions owning `dryv`.

Release cutover replaces the old distribution rather than merging implementations.

## Architecture tests

The core suite verifies:

- dependency/import direction and public/private namespaces;
- no old package imports;
- no CLI dependency below CLI;
- no plugin-specific imports in core;
- no process-global registry mutation;
- no plugin-defined semantic/facet/selector/context extension path;
- no target source renderer ports;
- generated text originates only from templates/macros/partials/static files;
- package installation/import in an isolated environment.
