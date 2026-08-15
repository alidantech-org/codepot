# Task 04 — Complete Policy, Failure, and Event semantics

Status: [ ]
Owner: `packages/python/dryv`
Depends on: Task 03
Validation: semantic relationship tests, transport round trips, architecture tests

## Goal

Complete three reusable canonical concepts without embedding transport/framework behavior into them.

## Policy

Policy is a reusable neutral rule or access requirement.

It may contain/reference:

- identity and documentation;
- typed inputs/context where required;
- composition of other Policies;
- approved principal/credential/role/access facts;
- guidance/tags/provenance.

Policies may be referenced by Operations, Views, Presentations, Workflows and other approved semantic relationships. They must not be tied to HTTP middleware, route guards, framework decorators or a specific authentication library.

## Failure

Failure is reusable typed failure meaning.

It may contain:

- semantic identity/code;
- meaning/documentation;
- optional payload Schema use;
- guidance/tags/provenance.

Operations reference Failures. Transport/execution facets may map a Failure to a status, wire error code or response representation, but those mappings must not redefine the Failure itself.

Avoid arbitrary untyped failure strings when a canonical Failure relationship is required.

## Event

Event is a first-class business occurrence.

It may contain:

- identity/name;
- optional payload Schema use;
- documentation;
- approved event facts;
- relevant Policy references where justified;
- guidance/tags/provenance.

### Relationship direction

The active relationship owner declares how it uses an Event:

```text
Operation emits Event
Operation listens to Event
Operation handles Event
Operation subscribes to Event
Workflow waits for Event
Workflow emits Event
View reacts to Event
```

Event must not author reverse lists of emitters/listeners/handlers/subscribers. Runtime derives those indexes later.

Events use ordinary Schema for payload typing. Do not create a separate event-payload schema root.

## Non-goals

- Do not implement broker/topic/queue infrastructure here.
- Do not define concrete HTTP status mappings inside Failure itself.
- Do not build authentication providers.
- Do not implement reverse relationship indexes; that belongs to the IR Runtime Feature task.

## Allowed paths

- `packages/python/dryv/src/dryv/ir/policies/**`
- `packages/python/dryv/src/dryv/ir/failures/**`
- `packages/python/dryv/src/dryv/ir/events/**`
- shared IR refs/kernel files required by these concepts
- corresponding tests/docs

## Acceptance criteria

- Policy, Failure and Event have independent canonical identity.
- Event payloads reuse Schema.
- Event does not own authored reverse usage lists.
- Failure remains transport-neutral while allowing later facet representations.
- Policies compose/reference deterministically without framework coupling.

## Validation

Add tests for Policy composition/reference validity, typed Failure payloads, Event payload refs, invalid Event reverse-authorship fields if legacy transport accepts them, and deterministic round trips. Run package/architecture tests and `git diff --check`.
