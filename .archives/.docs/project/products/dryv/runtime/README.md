# Dryv runtime

The `dryv` package owns canonical semantic contracts, validation, serialization and loading, runtime composition, planning, deterministic in-memory generation, and managed filesystem output.

Its approved architecture is centralized under [`../../../architecture`](../../../architecture/README.md). Runtime task ledgers are under [`../../../tasks/dryv/runtime`](../../../tasks/dryv/runtime/README.md).

The runtime does not own terminal presentation, authoring convenience APIs, target syntax, or template-engine syntax.
