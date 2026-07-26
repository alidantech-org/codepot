# 01 — Foundation and polished structure

## Purpose

The rewrite must first repair package structure and separation of concerns. The new runtime is an importable application library with explicit domain, application, port, plugin, configuration, and infrastructure boundaries.

## Proposed structure

```text
codepotg-v2/
├── README.md
├── pyproject.toml
├── docs/
├── src/codepotg/
│   ├── api/                # supported Python facade, requests, results, events
│   ├── application/        # use cases: configure, validate, inspect, generate
│   ├── config/             # location-aware documents, typed decoders, migrations
│   ├── domain/
│   │   ├── ir/             # neutral source-independent semantic model
│   │   └── generation/     # artifacts, selections, dependencies, plans
│   ├── plugins/            # descriptors, discovery, instance registries
│   ├── ports/              # source, language, engine, writer, cache, command ports
│   ├── runtime/            # immutable runtime and isolated generation sessions
│   ├── infrastructure/     # YAML, filesystem, entry points, Git, processes
│   └── cli/                # argument parsing and terminal presentation only
└── tests/
    ├── unit/
    ├── contract/
    ├── integration/
    ├── architecture/
    ├── fixtures/
    └── helpers/
```

## Dependency direction

```text
CLI / MCP / HTTP / playground
             ↓
       public Python API
             ↓
     application services
             ↓
       domain and ports
             ↑
 infrastructure and plugins
```

The domain must not import YAML, OpenAPI, Jinja, CLI, filesystem, subprocess, cache, Git, or framework packages. The CLI must contain no generation logic. Infrastructure implements ports and is composed at the outer boundary.

## Runtime rules

- No import-time source rewriting, `compile`/`exec`, monkey-patching, or `sys.modules` manipulation.
- No process-global mutable plugin registries or configuration.
- No module/package same-name collisions.
- No `sys.path` repair in the CLI.
- Every generation uses an isolated session with its own diagnostics, cancellation, plan, cache scope, and staged outputs.
- Frozen public models must not contain mutable internals.
- Errors and diagnostics are typed and carry source locations where applicable.
- Public API namespaces are explicit; internal modules are private and unsupported.

## Testing rules

- Unit tests cover one rule, function, or small class at a time.
- Contract suites are reused by every source adapter, language adapter, template engine, writer, and cache.
- Integration tests use small vertical fixtures rather than repository-sized projects.
- Architecture tests enforce dependency boundaries and public import rules.
- Legacy characterization tests stay under compatibility tests and never dictate the new internal design.
- Tests must not depend on network access, shell state, global environment mutation, ordering, or mutable global registries.
