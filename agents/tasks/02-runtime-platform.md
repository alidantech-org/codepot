# Phase 02 — Runtime and platform adapters

Status: [ ]
Issue: open when Phase 01 is complete
Depends on: Phase 01
Commit: pending
Validation: pending

## Goal

Implement the composition root and reusable infrastructure behind the approved ports without adding authoring, templating, generation, or CLI business logic.

## 02.1 Platform adapters

- [ ] Implement `NodeFileSystem` and `MemoryFileSystem` behind `FileSystemPort`.
- [ ] Implement YAML/JSON codecs behind `DataCodecPort`.
- [ ] Implement source hashing and deterministic source-graph fingerprints.
- [ ] Implement memory and filesystem cache adapters.
- [ ] Implement TypeScript module loading with consumer `tsconfig.json` support.
- [ ] Implement local, package, Git, and artifact source resolution.
- [ ] Implement command execution with cwd, env, optional failures, output capture, cancellation, and dry run.
- [ ] Implement changed-aware atomic writing and text/binary comparison modes.
- [ ] Implement deterministic clock and ID test adapters.

## 02.2 Runtime

- [ ] Define runtime interfaces and method contracts before implementation.
- [ ] Implement explicit factory-based dependency injection.
- [ ] Implement per-run context and `AbortSignal` propagation.
- [ ] Implement typed request dispatch without a generic service locator.
- [ ] Implement feature/capability discovery.
- [ ] Implement a typed event bus for observation only.
- [ ] Isolate listener failures and preserve sequence ordering.

## 02.3 Validation

- [ ] Unit-test every adapter through its port contract.
- [ ] Run identical filesystem behavior tests against Node and memory adapters.
- [ ] Verify domain modules can be constructed entirely with memory adapters.
- [ ] Verify no domain implementation directly imports Node I/O or process APIs.
- [ ] Typecheck, build, and package validation pass.
- [ ] Record issue, commit, and evidence before marking complete.
