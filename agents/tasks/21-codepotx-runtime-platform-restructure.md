# Task 21 — Runtime and platform modularization

Status: [ ]
Issue: open when ready
Depends on: Task 20
Commit: pending
Validation: pending

## Goal

Replace growing runtime switch dispatch and flat platform adapters with typed operation handlers and capability-based Node, memory, and shared infrastructure folders without changing runtime requests, events, cancellation, or default composition.

## Target structure

```text
src/runtime/
├── context/
├── dispatch/
├── composition/
├── runtime.ts
└── index.ts

src/platform/
├── node/
├── memory/
├── shared/
├── create-platform-services.ts
└── index.ts
```

## Runtime work

- [ ] Define a typed operation-handler contract and registry.
- [ ] Register authoring, templating, generation, and runtime feature handlers by operation kind.
- [ ] Replace central `as never` dispatch casts with typed handler mapping.
- [ ] Preserve exhaustive operation coverage at compile time.
- [ ] Move run context storage into `runtime/context/`.
- [ ] Move default feature declarations and runtime composition into `runtime/composition/`.
- [ ] Keep runtime responsible only for context, timing, cancellation, event envelopes, error normalization, feature discovery, and dispatch.
- [ ] Preserve listener isolation and ordered events.

## Platform work

- [ ] Group Node filesystem, command, module, source, and cache adapters by capability.
- [ ] Group memory filesystem, command, module, source, and cache adapters by capability.
- [ ] Move adapter-independent primitives into focused `shared/` folders only when reused.
- [ ] Preserve one default platform composition factory.
- [ ] Preserve deterministic fixed clock and sequential ID adapters.
- [ ] Keep business validation and orchestration out of platform.
- [ ] Keep all domain I/O behind existing contract ports.

## Type-safety requirements

- [ ] Runtime operation request and response inference remains exact by operation kind.
- [ ] Handler registration rejects missing, duplicate, or mismatched handlers at compile time or startup validation.
- [ ] No generic service locator is introduced.
- [ ] No `any`, `@ts-ignore`, or broad runtime casts replace current dispatch casts.
- [ ] Memory adapters continue to satisfy the same ports as Node adapters.

## Acceptance criteria

- [ ] Runtime dispatch has no central unsafe `as never` chain.
- [ ] Adding a new operation requires a typed handler rather than editing unrelated dispatch logic.
- [ ] Node and memory adapters are easy to locate by capability.
- [ ] Existing runtime/platform tests and event snapshots remain equivalent.
- [ ] `codepotx/runtime` and `codepotx/platform` exports remain compatible and explicit.

## Validation

```bash
pnpm --filter codepotx typecheck
pnpm --filter codepotx test
pnpm --filter codepotx build
pnpm --filter codepotx package:lint
```
