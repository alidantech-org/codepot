# 01 — Foundation and polished structure

The v2 runtime is a clean, importable Python application with explicit public API, application, domain, port, plugin, runtime, infrastructure, and CLI boundaries.

## Documents

- [`01-package-architecture.md`](01-package-architecture.md) — complete source layout, responsibilities, dependency direction, distribution topology, namespace cutover, and architecture tests.
- [`02-public-python-api.md`](02-public-python-api.md) — facade, operations, sessions, sync/async behavior, memory output, events, results, and server-safe use.
- [`03-diagnostics-events-results.md`](03-diagnostics-events-results.md) — diagnostic codes/spans, event model, cancellation, result status, and error boundaries.

## Non-negotiable rules

- No import-time source rewriting, `compile`/`exec`, monkey patching, `sys.modules`, or CLI `sys.path` repair.
- No process-global mutable registries or configuration.
- No old generator imports or compatibility runtime.
- No same-name module/package collisions.
- No CLI business logic below the CLI layer.
- Frozen public models contain immutable internals.
- Every operation has an isolated session.
- Tests are small, modular, deterministic, and independent from network/global state.

## Planned core layout

```text
src/dryv/
├── api/
├── application/
├── config/
├── domain/ir/
├── domain/generation/
├── plugins/
├── ports/
├── runtime/
├── infrastructure/
└── cli/
```

Read the approved architecture before implementing any folder.
