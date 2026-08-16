# Task 20 — Rewrite Dryv Runtime as the composition root

Status: [x]
Owner: `packages/python/dryv`
Depends on: Tasks 08–19
Validation: end-to-end runtime tests with fake sessions/resources, architecture tests

> Implementation is complete on `develop`. Executable certification is still pending because the connected repository environment exposes no checkout/test runner. See [`../PROGRESS-18-25.md`](../PROGRESS-18-25.md).

## Goal

Rewrite `dryv.runtime` into a small composition/control layer that coordinates approved Features and owns the build lifecycle without absorbing Feature implementation details.

## Runtime composition

Runtime composes public Feature facades for:

```text
serialization
project
resources
hashing
ir
packs
planning
cache
authoring
templating
scheduling
artifacts
diagnostics
```

Runtime is responsible for choosing when those capabilities are used and for supplying already-established Author/Render Sessions to the relevant Features.

## Build lifecycle

A build should conceptually follow:

```text
receive BuildInput/resources
→ normalize dryv.yaml
→ acquire Canonical IR
   ├── load supplied IR
   └── or request IR through Author Session
→ validate/index/resolve IR
→ load/normalize packs
→ plan selections/context/artifacts/dependencies
→ compute cache identities
→ schedule ready render work
→ validate Render Results
→ classify artifacts/write instructions
→ emit diagnostics/progress/artifact stream/build result
```

Runtime may overlap later independent phases where safe, but the ownership order above must remain explainable.

## Build contracts

Define stable engine contracts for:

- `BuildRequest`/input resources;
- previous managed outputs;
- available Author/Render Sessions;
- cache/build modes;
- progress/diagnostic events;
- cancellation;
- artifact/write-instruction stream;
- final `render_complete` result.

These are engine contracts. HTTP/WS wire hosting belongs to the outer API package.

## Selection of external sessions

Runtime selects a compatible session based on explicit project/pack requirements and advertised capabilities. Templating/Authoring Features do not choose connections themselves.

Selection must be deterministic where multiple equivalent sessions exist, or Scheduling must use an explicit fair/capacity policy with traceable decisions.

## Explainability

Runtime must surface a trace that can answer:

```text
where IR came from
which pack/template selected an item
which context dependencies were used
why cache hit/missed
which render session handled a job
what artifact was produced
why an artifact is create/update/unchanged/delete-managed
```

## Non-goals

- Do not host HTTP/WS.
- Do not read/write user project files.
- Do not implement template engines or author compilers.
- Do not duplicate Feature internals inside Runtime.

## Allowed paths

- `packages/python/dryv/src/dryv/runtime/**`
- Runtime-facing public contracts
- legacy application/session/composition modules being migrated
- corresponding tests/docs

## Acceptance criteria

- Runtime is the only component coordinating multiple Features.
- a complete build works with supplied in-memory resources and fake Author/Render Sessions.
- no direct project filesystem writes occur.
- no concrete network/template/author implementation dependency exists.
- build trace and cancellation propagate end to end.

## Validation

Create end-to-end tests for precompiled IR build, Author Session build, cache hit/miss, multiple renderer capacity, cancellation, render failure and artifact classification. Run the complete Dryv suite, architecture tests and `git diff --check`.
