# Phase 02 — Runtime and platform adapters

Status: [x]
Issue: #4 closed as completed
Depends on: Phase 01 complete
Commits: `eea311de78bb32cdf27b0444850cc0169c471bd7`, `46add634861b1e29c54cf4669c9c572fd9ca1b31`, `0217170f27a2e45c6b1b551aca9757253e8b5073`, `90b716289bb4f9e65d655ec7b806fb2fa7f73a60`
Validation: strict TypeScript checks, isolated declaration emission, and 13 focused runtime/platform tests passed; GitHub blob, content, package-export, and commit comparisons verified the committed implementation.

## Goal

Implement the composition root and reusable infrastructure behind the approved ports without adding authoring, templating, generation, or CLI business logic.

## 02.1 Platform adapters

- [x] Implement `NodeFileSystem` and `MemoryFileSystem` behind `FileSystemPort`.
- [x] Implement YAML/JSON codecs behind `DataCodecPort`.
- [x] Implement canonical SHA-256 hashing and deterministic source-graph fingerprints.
- [x] Implement memory and filesystem cache adapters with encoded payloads and expiry.
- [x] Implement TypeScript module loading through `tsx` with consumer `tsconfig.json` support and reachable-import tracking.
- [x] Implement local, package, Git, artifact, and memory source resolution.
- [x] Implement command execution with cwd, env, output capture, cancellation, and dry run.
- [x] Implement changed-aware atomic writing and exact, layout-insensitive, and raw comparison modes.
- [x] Implement production and deterministic clock/ID adapters.
- [x] Implement memory command, module, filesystem, cache, and source adapters.

## 02.2 Runtime

- [x] Runtime interfaces and method contracts were completed in Phase 01.
- [x] Implement explicit factory-based dependency injection.
- [x] Implement per-run context using `AsyncLocalStorage` and cancellation propagation.
- [x] Implement typed request dispatch without a generic service locator.
- [x] Implement feature/capability discovery.
- [x] Implement a typed event bus for observation only.
- [x] Isolate listener failures and preserve publication ordering.
- [x] Convert cancellations and unexpected failures into structured runtime diagnostics.
- [x] Export advanced runtime and platform entrypoints through `codepotx/runtime` and `codepotx/platform`.

## 02.3 Validation

- [x] Test every implemented adapter through its contract boundary.
- [x] Run identical core filesystem behavior against Node and memory adapters.
- [x] Verify runtime/platform construction with memory adapters.
- [x] Verify domain-facing contracts do not import concrete platform implementations.
- [x] Verify Git resolution using a real temporary local Git repository.
- [x] Verify module loading and cache identity.
- [x] Verify event ordering and observer-error isolation.
- [x] Verify command output, dry-run behavior, and cancellation.
- [x] Verify changed-aware managed and immutable writes.
- [x] Strict typecheck and declaration emission pass.
- [x] Record issue, commits, and evidence before marking complete.

## Architecture decisions

- Runtime composition uses constructor/factory injection, not decorators, reflection, or a service locator.
- `SequentialEventBus` is observational: listener failures are isolated and cannot alter required control flow.
- `RunContextStore` carries correlation data only; domain state stays in explicit requests and results.
- Atomic replacement is an internal filesystem capability (`AtomicFileSystemPort`) so the stable public `FileSystemPort` remains minimal.
- `TsxModuleLoader` loads only the selected entry and reachable imports; it does not build the consumer application.
- Source resolution is shared by authoring and templating and supports local, package, Git, artifact, and memory sources.
- Node and memory service factories expose the same `PlatformServices` shape.
- Node's built-in async glob is used at the package's Node `>=22.18.0` floor, avoiding another glob dependency.

## Validation evidence

- Strict `tsc` checks passed with exact optional properties, isolated modules/declarations, no unchecked indexed access, and unused-code checks.
- Declaration-only emission passed for contract, runtime, platform, and root entrypoints.
- Test run: 13 tests, 13 passed, 0 failed, 0 skipped.
- The test suite covers event ordering, Node/memory filesystem parity, changed-aware writing, cache expiry, command cancellation, memory substitutes, JSON-safe codecs, deterministic hashing, filesystem cache, module loading, all five source kinds, runtime dispatch, and structured cancellation.
- GitHub comparison from `8f033502609825daa6dad39f625b69226fae0ccc` to `90b716289bb4f9e65d655ec7b806fb2fa7f73a60` verified all implementation, test, export, dependency, Turbo, and build-entry changes.
- GitHub content reads verified the source resolver and published `codepotx/runtime` and `codepotx/platform` package subpaths.
- Local validation used Node 22.16.0, where async glob still emitted an experimental warning. The published package requires Node 22.18.0+, where that API is stable.
- Full `pnpm pack`, Publint, Are The Types Wrong, and pinned dependency validation remain the explicit Phase 07 release gate because this connector environment cannot install workspace dependencies.
