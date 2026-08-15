# Task 05 — Complete Operation I/O, relationships, effects, and facets

Status: [x]
Owner: `packages/python/dryv`
Depends on: Task 04
Validation: operation semantic tests, relationship tests, transport round trips

> Implementation is complete on `develop`. External executable certification is still pending because the connected environment exposes no repository checkout or CI runner. See [`../PROGRESS-00-10.md`](../PROGRESS-00-10.md).

## Goal

Harden `Operation` as the neutral behavior concept used across transports, workflows, events and presentations.

Canonical shape:

```text
Operation
├── Inputs
├── Outputs
├── Failures
├── Policies
├── Effects
├── Event relationships
├── Operation relationships
└── Facets
```

## Input and output semantics

Operations must naturally support:

```text
no input
one input
multiple inputs
named inputs

no output
one output
multiple outputs
named outputs
```

Absence of I/O is semantic absence, not a fake empty Schema. Inputs/outputs that carry data reference ordinary Schemas.

The model must remain capable of multiple named inputs/outputs where required by authored meaning; do not force all operations into a single request/response convention.

## Subject and Schema relationships

An Operation may be associated with one or more subject Schemas for authoring/discovery while remaining independently owned by its Group.

Examples:

```text
CreatePool subjects: [Pool]
Checkout subjects: [Cart, Order, Payment]
```

Schema must not canonically own Operations. Runtime may later derive `schema.operations` style context.

## Event relationships

Operation owns forward relationships such as:

```text
emits Event
listens to Event
handles Event
subscribes to Event
```

The exact distinction between listen/handle/subscribe must be represented only if it carries stable neutral meaning; do not create redundant generated-role roots.

## Operation relationships

Support typed, explicit relationships needed for composition, such as approved forms of:

```text
invokes Operation
requires Operation
delegates to Operation
runs before Operation
runs after Operation
triggers Workflow
```

Names must remain consistent with the canonical vocabulary approved during implementation; do not add a generic untyped relationship bag.

## Failures and Policies

Operations reference canonical Failure and Policy concepts. Operation-specific representation facts belong to facets where appropriate.

## Effects and execution facts

Preserve neutral effect/execution meaning required by the recovered design. Typed facts may include transaction/consistency, sync/async intent, retry, timeout, idempotency or concurrency only where already approved by the current model or explicitly accepted during task execution. Do not create infrastructure root concepts for these.

## Facets

Facets remain closed typed contracts. The supported family must cover current approved needs including HTTP, access, event transport, execution, trigger and scheduling where implemented.

An HTTP facet may express neutral facts such as method, path, input/output bindings, status representations, headers, cookies, media types and serialization.

An event transport facet may express topic/channel binding, serialization and approved delivery facts for an Event use.

Do not put framework controller/service/request-object meaning into facets.

## Non-goals

- Do not create canonical Command, Query, Listener, Handler, Job, Controller, Service or Repository roots.
- Do not implement runtime dispatch/execution.
- Do not implement template selection.
- Do not render target-language `void`/`None`/`Unit`; packs do that later.

## Allowed paths

- `packages/python/dryv/src/dryv/ir/operations/**`
- facet/effect files under canonical IR
- shared refs required by Operation
- corresponding tests/docs

## Acceptance criteria

- Operation supports explicit semantic absence of input and output.
- Multiple/named I/O remains representable.
- Operation owns forward Event/Operation relationships.
- Failures/Policies use typed canonical refs.
- Facets are typed and target/framework neutral.
- Invalid refs, duplicate I/O names, cycles where forbidden, and invalid facet combinations fail clearly.

## Validation

Add tests for no-I/O, one/many named I/O, Schema subjects, Event emission/listening, Operation dependencies/hooks, Failures/Policies and current facet contracts. Run full IR/architecture tests and `git diff --check`.
