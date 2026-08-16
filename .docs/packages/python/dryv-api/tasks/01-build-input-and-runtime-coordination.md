# Task 01 — Build input and Runtime coordination

Status: [ ]
Owner: `packages/python/dryv-api`
Depends on: Task 00

## Goal

Implement the stateless V1 build lifecycle that accepts the three approved inputs, normalizes logical resources and invokes Dryv Runtime to obtain `GenerationPlan` while streaming Runtime progress to API build events.

## Build inputs

A build is created from:

```text
dryv.yaml
Canonical Dryv IR
pack bundles
```

Local filesystem paths are resolved by the Project Client before upload. The API receives logical resources and content, not the user's project root.

## Resource normalization

`resources/bundle.py` decodes/normalizes uploaded config, IR and pack bundle resources.

`resources/store.py` owns request/build-scoped logical content storage for V1. Design identity around server-verified content hashes so future content-addressed reuse can be added without changing Runtime semantics.

Reject transport-level problems such as duplicate resource IDs, malformed bundle paths and claimed-hash/content mismatches before Runtime invocation.

Do not validate Canonical IR or pack semantics here; Runtime owns those meanings.

## BuildSession

`builds/session.py` owns one active build state:

```text
build id
status
normalized Runtime input
GenerationPlan when available
cancellation
execution/delivery state
event stream
```

It must not become a semantic model.

`builds/manager.py` owns create/get/cancel/release for active sessions. V1 may keep active build state in memory.

## Runtime invocation

The API creates/uses Dryv Runtime through its public contracts and passes only normalized Runtime input.

Runtime progress/diagnostics are translated into API build events without changing meaning.

Required ordering:

```text
request accepted
    ↓
resources normalized
    ↓
Runtime starts
    ↓
config / IR / packs validated by Runtime
    ↓
GenerationPlan returned
    ↓
build becomes ready for renderer prerequisite checks
```

## Forbidden API semantics

Do not:

- derive `planningCandidates` in API;
- independently evaluate pack selectors;
- construct template context in API;
- choose planned artifact paths in API;
- execute author source;
- read a user project filesystem;
- pass local apply state into Runtime.

## Events

`builds/events.py` owns API-level build lifecycle events. Runtime events may be wrapped with build identity but must remain semantically faithful.

Examples include build accepted/started, Runtime progress, plan ready, diagnostic, cancelled and failed.

## Code-size enforcement

Every production file must remain at or below 500 lines and follow the required final API tree.

## No-test gate

Do not create, modify or rewrite tests. Test work remains blocked until explicit production-code approval.

## Completion evidence

Inspect production code and demonstrate the direct data flow:

```text
uploaded config + IR + pack bundles
    → normalized RuntimeInput
    → DryvRuntime
    → GenerationPlan
```

Confirm no semantic planning logic exists in `dryv-api`, no project filesystem access exists, no file exceeds 500 lines and no tests were changed.
