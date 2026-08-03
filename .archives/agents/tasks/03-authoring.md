# Phase 03 — Authoring parity and canonical compiler

Status: [x]
Issue: #5
Depends on: Shared contracts, module loader, source resolver, cache, hashing, diagnostics, events
Commits: `1942a954c9ffddb2f0a3fc5e39835d14b7e02b23`, `779f19d212d5ae1670abd7b2fcb56889492b43c8`, `2fef7f5ebe8c0a0602170624600327b295ab1881`
Validation: strict synthetic TypeScript contract check passed for the complete authoring module; focused schema and refs/property tests passed; an import-only migrated contract fixture compiles directly into a deterministic JSON-serializable `CompiledAuthoringArtifact`.

## Completed

- [x] Preserved `z` compatibility and preferred `schema` namespace.
- [x] Ported properties, refs, schemas, components, access, hooks, entities, relations, routes, resources, frontends, and version contracts.
- [x] Added `defineCodepotConfig` and deprecated `definePackageConfig` compatibility.
- [x] Added source, artifact, cache, validation, inspect, and compile operations behind `AuthoringPort`.
- [x] Added canonical compiler that does not require an OpenAPI intermediate representation.
- [x] Validated duplicate operation IDs and cache invalidation operation references.
- [x] Stable artifacts exclude live Zod instances, builders, maps, sets, and functions.
- [x] Added import-only migration fixture and stable artifact serialization coverage.
