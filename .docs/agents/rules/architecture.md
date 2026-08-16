# Architecture rules

## Governing flow

```text
Authoring
    ↓
Canonical Dryv Runtime IR
    ↓
Templating
    ↓
Usage and generated output
```

## Ownership

- Authoring defines software meaning and compiles it into Canonical Dryv Runtime IR.
- Authoring does not generate application source, select packs, define output paths, write generated files or serialize Runtime IR.
- Canonical Dryv Runtime IR is the only semantic authority.
- Dryv Engine owns canonical validation/loading/indexing, `dryv.yaml` meaning, pack meaning, selection, dependency planning, context construction, output planning, deterministic hashing/caching and Runtime diagnostics/trace.
- Dryv Runtime stops at a complete `GenerationPlan`.
- Packs define how canonical meaning maps to templates, context and planned artifacts; packs do not redefine software meaning.
- Render Clients own template-language validation and every rendered output byte. They receive template + canonical context + planned output metadata, not Canonical IR semantics.
- `dryv-api` owns build transport/execution coordination: resources, build sessions, renderer connections/capacity, template preflight coordination, bounded scheduling/backpressure, progress streaming and optional output bundles.
- Project Clients own local resource collection, diff, safe extraction/apply, project filesystem mutation and local shell/Git work.
- A CLI, DevAuto or another AI integration is a Project Client/tooling layer, not a competing generation engine.

## Required properties

- Deterministic: equal locked semantic/template/renderer inputs produce equal plans and output identities.
- Explainable: selection, context, dependencies, paths, hashes and provenance are inspectable.
- Portable: canonical meaning and pack contracts do not depend on hidden machine state or user project roots.
- Bounded: network execution and artifact transfer use explicit capacity/backpressure; unbounded buffering is forbidden.
- Closed: API, clients and renderers cannot invent Canonical IR semantics or hidden selection rules.
- Deployable: the same Engine may be hosted locally or behind `dryv-api` without changing semantic behavior.

## Forbidden ownership leaks

- No Author Backend execution inside Dryv Runtime.
- No Render Client connection/session inside Dryv Runtime.
- No template engine execution inside Dryv Runtime.
- No generated artifact byte ownership or ZIP creation inside Dryv Runtime.
- No project filesystem writes in `dryv` or `dryv-api`.
- No API-side competing pack selection/context construction.
- No compatibility shims that preserve a superseded architectural owner after an approved refactor removes it.

## Architecture changes

Do not silently change these boundaries. Obtain explicit user approval before moving ownership or adding a new architectural layer.

For the active Dryv refactor, `.docs/packages/python/dryv/ARCHITECTURE.md` and `IMPLEMENTATION-RULES.md` are the detailed canonical contracts.
