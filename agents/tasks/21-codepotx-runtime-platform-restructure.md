# Task 21 — Runtime and platform modularization

Status: [~]
Issue: #19 open
Depends on: Task 20 complete
Commits: runtime context/dispatch/composition and typed event work from `5f2a831fc7a996bfc86863694c0b1083f52cbad6` through `3a990146427efffee82799f23e46730605254ec5`; platform ownership migration through `27c76ceee65ccf5e8e4f0184e525b07fdf62c797`; guardrails through `2943af7417f8ca646a231f0b6f2b9514d8a3b28b`
Validation: implementation and static guardrails are committed. Strict typecheck, behavioral tests, build, and package validation remain part of the combined Tasks 21–23 gate.

## Goal

Replace central runtime switch dispatch and flat platform adapters with typed operation handlers and capability-based Node, memory, and shared infrastructure folders without changing runtime requests, events, cancellation, or default composition.

## Runtime completion

- [x] Define a typed operation-handler contract and exhaustive registry.
- [x] Register every authoring, templating, generation, and runtime feature operation by kind.
- [x] Remove the central `as never` dispatch chain.
- [x] Preserve compile-time operation coverage through `RuntimeOperationHandlerRegistry` and `satisfies`.
- [x] Move run context creation/storage into `runtime/context/`.
- [x] Move default features and composition into `runtime/composition/`.
- [x] Keep runtime focused on context, timing, cancellation, typed lifecycle events, failure normalization, feature discovery, and dispatch.
- [x] Preserve ordered event publication and listener isolation.

## Platform completion

- [x] Group Node filesystem, command, module, cache, and source resolver ownership under `platform/node/`.
- [x] Group memory filesystem, command, module, cache, and source registry ownership under `platform/memory/`.
- [x] Move shared errors, cancellation, codec, events, writer, hashing, paths, clocks, IDs, and source contracts under `platform/shared/`.
- [x] Rewire default and memory platform factories to capability folders.
- [x] Preserve fixed clocks, sequential IDs, default composition, and all existing ports.
- [x] Convert moved flat implementation files to thin compatibility shims.
- [x] Keep business validation and domain orchestration outside platform.

## Type-safety and acceptance

- [x] Runtime request and result types remain indexed by exact operation kind.
- [x] Handler registration rejects missing or mismatched handlers through the mapped registry.
- [x] No service locator, `any`, `@ts-ignore`, or new broad dispatch cast was introduced.
- [x] Adding an operation requires adding a typed handler, not editing runtime lifecycle code.
- [x] Runtime and platform package facades remain explicit and compatible.
- [ ] Confirm strict typecheck, adapter parity, runtime behavior, events, build, Publint, and ESM package checks in the combined gate.

## Validation

```bash
pnpm --filter codepotx check
pnpm --filter codepotx-cli check
```
