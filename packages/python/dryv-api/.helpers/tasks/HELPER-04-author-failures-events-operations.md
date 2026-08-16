# HELPER-04 — Failures, events and operations

Status: TODO
Prerequisite: HELPER-03 DONE.

## Goal
Implement first-class behavior authoring around the current canonical Failure, Event and Operation models.

## Scope
Implement `features/failures/*`, `features/events/*`, and `features/operations/*` including operation inputs, outputs, effects, facets and references.

Required capabilities:
- named failures referenced by operations without legacy OperationFailure compatibility values;
- events with explicit payload/relationships/effects supported by current IR;
- operation inputs and named outputs with schema/type references;
- operation failure/event/effect relationships;
- operation facets/metadata only where they represent canonical software meaning;
- deterministic compile order and diagnostics for invalid relationships.

## Enforcement
Do not model HTTP routes/framework handlers as operation semantics unless represented canonically. No generator/template behavior. No old OpenAPI route compiler copied into Author.

## Completion
Failure/Event/Operation declarations are ergonomic but compile to explicit canonical items and IDs, with all cross-references validated. No tests yet.