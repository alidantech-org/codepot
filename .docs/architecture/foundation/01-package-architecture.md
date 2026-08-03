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
├── diagnostics/
├── domain/
│   ├── ir/
│   └── generation/
├── generation/
├── infrastructure/
├── ir/
├── plugins/
├── ports/
├── runtime/
├── testing/
└── versions/
```

The runtime package contains no `cli/` package and no console script.

## Runtime facade

`dryv.runtime.DryvRuntime` is the primary in-process interface:

```text
DryvRuntime
├── snapshot
├── plan
├── generate
└── generate_to_files
```

A runtime owns one immutable plugin graph. Frontends may discover installed plugins or inject an explicit graph for tests and embedded hosts.

The runtime returns structured operation results and immutable inspection data. It contains no terminal colors, prompts, spinners, command parser, or output formatting.

## Responsibilities

### `api`

Stable operation results, cancellation, events, and supported public primitives.

### `application`

Use cases for project loading, validation, planning, rendering, and writing. Application services depend on domain contracts and ports.

### `config`

Strict project and pack decoding, typed options/bindings, path validation, and configuration diagnostics.

### `domain.ir`

The closed source-neutral semantic kernel:

```text
contract and groups
semantic identity, names, provenance, tags, and guidance
structural schemas and uses
operations, failures, effects, and known facets
views and parts
storage mappings
policies and access
application events and execution hooks
value sources
workflows and compensation
presentations and view placement
```

It contains no source provider implementation, target syntax, template engine, filesystem, command executor, or interface concern.

### `domain.generation`

Selection, artifact identity, dependencies, destinations, module/path facts, explanation, impact, and ownership intent. It does not render target-language text.

### `plugins`

Public plugin descriptors, compatibility, and runtime registry validation. Plugins cannot extend the semantic kernel.

### `ports`

Public contracts for source adapters, target adapters, template engines, managed writers, and future approved providers/infrastructure.

### `runtime`

Immutable plugin composition, generation sessions, runtime inspection, and the public `DryvRuntime` facade.

### `infrastructure`

Safe YAML/JSON, canonical IR loading, pack discovery, plugin entry-point loading, archive/memory/filesystem writers, and ownership state.

## Standalone CLI layout

```text
packages/python/dryv-cli/
├── src/dryv_cli/
│   ├── commands/
│   ├── presentation/
│   ├── prompts/
│   ├── services/
│   ├── app.py
│   ├── main.py
│   └── __main__.py
└── tests/
```

`dryv-cli` owns:

- Click command parsing and help dispatch;
- Rich colors, spinners, trees, diagnostics, and summaries;
- Questionary interactive confirmation;
- stable JSON presentation;
- CLI exit-code policy.

It imports only public Dryv contracts and contains no planning, rendering, writer, plugin-discovery, or semantic implementation.

## Dependency direction

```text
dryv-cli / IDE / MCP / HTTP / notebook / host application
                         │
                         ▼
                    DryvRuntime
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
- runtime composition may select approved infrastructure implementations;
- interfaces consume only public runtime APIs;
- plugin packages consume only published contracts;
- only Dryv core defines semantic objects, facets, selectors, and contexts;
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

Reusable packs remain independently versioned artifacts.

## Architecture tests

The suites verify:

- dependency direction and public/private namespaces;
- no archived implementation imports;
- no terminal frontend or console script in `dryv`;
- no private Dryv imports from `dryv-cli`;
- no direct Python `print()` or `input()` in CLI source;
- no Rich panels or box borders;
- no stale `.gitkeep` beside implemented source/tests;
- no process-global runtime registry;
- generated text originates only from packs.
