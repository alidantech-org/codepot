# Task 27 — Build the GenerationPlan Runtime

Status: [ ]
Owner: `packages/python/dryv`
Depends on: Task 26

## Goal

Implement the final Dryv Runtime so `dryv.yaml + Canonical Dryv IR + normalized pack resources` deterministically produce one complete `GenerationPlan` and transport-neutral progress/diagnostics.

Runtime stops at the plan. It must not render templates or own generated artifact bytes.

## Required public Runtime flow

```text
RuntimeInput
    ↓
load/validate usage configuration
    ↓
load/validate/index Canonical IR
    ↓
load/validate packs
    ↓
resolve options/relationships
    ↓
evaluate template selection
    ↓
build semantic + generation dependency graph
    ↓
construct canonical contexts
    ↓
resolve planned output paths
    ↓
hash deterministic inputs
    ↓
GenerationPlan
```

## Required Runtime files

```text
dryv/runtime/
├── __init__.py
├── contracts.py
├── events.py
└── runtime.py
```

### `contracts.py`

Own only Runtime boundary data such as:

```text
RuntimeInput
RuntimeResource
RuntimePack
GenerationPlan
RenderJob
RendererRequirement
TemplateReference
ContextContract
PlannedArtifact
PlanDependency
RuntimeDiagnostic
RuntimeResult
```

Do not add HTTP/WebSocket/client/session objects.

### `events.py`

Own transport-neutral Runtime events and the event sink/observer contract.

Events may describe stages such as config/IR/pack loading, graph construction, planning progress, context creation, diagnostics and plan completion. They must not contain WebSocket-specific framing.

### `runtime.py`

Own the small Runtime composition root. It coordinates approved Features and returns the complete plan.

If this file approaches 500 lines, split logic into the owning Feature rather than creating another Runtime facade/service layer.

## Planning completeness

Every `RenderJob` must carry enough deterministic data for `dryv-api` to execute it without reinterpreting pack semantics:

- stable job identity;
- semantic subject identity/kind;
- pack/template selection reason;
- renderer capability requirement;
- template logical resource identity and content hash;
- canonical context values;
- context contract/version/hash;
- planned artifact IDs and normalized project-relative paths;
- deterministic job/artifact dependencies;
- deterministic plan ordering/provenance.

## Context rule

Runtime owns context meaning. Render Clients must receive JSON-like canonical context, not Canonical IR model objects.

Context hashes must reflect only output-relevant deterministic input so later cache/stateful work can avoid unrelated rerenders.

## Pack rule

Only Packs/Planning may interpret `dryv.pack.yaml` selection/binding/output semantics. `dryv-api` must not need to parse pack rules again.

## Runtime progress

Runtime accepts an observer/sink and emits pure-data progress/diagnostic events. Event delivery must not block semantic correctness or introduce transport dependencies.

## Forbidden implementation

Do not:

- execute Jinja/Handlebars/another template engine;
- connect to Render Clients;
- inspect renderer URLs/capacity;
- build artifact byte streams;
- compare local files;
- create ZIP/TAR bundles;
- write files;
- execute shell/Git;
- add compatibility aliases for the removed Runtime architecture.

## Code-size enforcement

Every production source file must remain at or below 500 lines. Use the exact final folder structure from `IMPLEMENTATION-RULES.md`; do not invent generic buckets.

## No-test gate

Do not create, modify or rewrite tests in this task. Production code is reviewed first. Test design begins only after explicit user approval.

## Allowed paths

- `packages/python/dryv/**`
- `.docs/packages/python/dryv/**` only for factual progress/status corrections

## Completion evidence

Before marking complete, inspect and demonstrate through code/data flow that:

- Runtime can accept normalized usage config, Canonical IR and pack resources;
- Runtime produces a complete deterministic `GenerationPlan`;
- all renderer execution concerns are absent from Engine;
- Runtime progress is transport-neutral;
- no production source file exceeds 500 lines;
- no tests were added or modified.

After Task 27, the Engine production code is structurally ready for `dryv-api`. Do not add test work until the explicit approval gate is lifted.
