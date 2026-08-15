# Task 07 — Complete Workflow, Presentation, and cross-cutting semantics

Status: [ ]
Owner: `packages/python/dryv`
Depends on: Task 06
Validation: workflow graph tests, presentation relationship tests, transport round trips

## Goal

Complete the higher-order composition roots while preserving the recovered authoring design: advanced behavior should compose existing canonical concepts rather than create a new root for every implementation pattern.

## Workflow

`Workflow` is a compositional behavior concept. It may contain/reference:

```text
Schema-typed inputs/outputs
Operation steps
Event waits
Event emissions
Policy conditions
Failure paths
transitions
decisions
branches
waits
compensation Operations
child Workflows
guidance/tags/provenance
```

The internal workflow model must be typed and deterministic, but workflow steps/transitions/decisions do not automatically become Contract-level root concepts.

Support both simple sequences and richer branches/waits/compensation without embedding a specific workflow engine.

Example meaning:

```text
CreateOrder
→ ReserveInventory
→ Decision
    ├── CapturePayment
    └── Wait for PaymentConfirmed
→ CompleteOrder

on failure:
    ReleaseInventory
```

## Presentation

`Presentation` composes an application surface and may reference:

```text
channel/surface identity
Views
View placements
addresses/routes/commands as neutral addresses
navigation
shell relationships
Policies/access
Operations
Events
Workflows
guidance/tags/provenance
```

It can represent web, mobile, CLI, desktop, documentation or conversational surfaces without containing framework names, CSS/widget trees, component libraries or state-management libraries.

Preserve the current contract-level ownership unless a separately approved architecture decision changes it. Do not silently relocate Presentation under Group.

## Cross-cutting information

Canonical cross-cutting contracts must support:

- namespaced immutable tags as hints, not behavior;
- categorized guidance such as explain/implement/warn/security/persistence/caching/testing/observability/UX/accessibility;
- documentation;
- provenance/origin information sufficient to trace authored meaning into canonical IR and later generated artifacts;
- typed refs rather than global registries.

Tags/guidance must not silently activate runtime/generation behavior.

## Non-goals

- Do not create canonical Saga, ProcessManager, Reducer, ViewModel, Page, Screen, Component or StateMachine roots.
- Do not implement a workflow execution engine.
- Do not implement frontend rendering.
- Do not finalize template variable names/selection syntax.

## Allowed paths

- `packages/python/dryv/src/dryv/ir/workflows/**`
- `packages/python/dryv/src/dryv/ir/presentations/**`
- `packages/python/dryv/src/dryv/ir/cross_cutting/**`
- shared IR refs/kernel required by these concepts
- corresponding tests/docs

## Acceptance criteria

- Workflow can compose Operations, Events, Policies, Failures and child Workflows with deterministic typed internal nodes.
- Workflow input/output uses ordinary Schema.
- Presentation composes Views and related semantic behavior without framework coupling.
- tags/guidance/provenance are portable and behavior-neutral.
- invalid workflow references/cycles where forbidden are diagnosed clearly.

## Validation

Add tests for sequence/branch/wait/compensation/child-workflow cases, Presentation placements/navigation references, provenance preservation and deterministic round trips. Run full IR/architecture tests and `git diff --check`.
