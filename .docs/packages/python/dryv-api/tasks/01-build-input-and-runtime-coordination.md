# Task 01 — Build input and Runtime coordination

Status: [x]
Owner: `packages/python/dryv-api`
Depends on: Task 00

## Goal

Implement the stateless V1 build lifecycle that accepts the three approved inputs, normalizes logical resources and invokes Dryv Runtime to obtain `GenerationPlan` while preserving Runtime progress as API build events.

## Implemented data flow

```text
uploaded dryv.yaml
+ Canonical Dryv IR
+ pack bundles
+ explicit additional resources
        ↓
BuildResourceUpload / PackBundleUpload
        ↓
ResourceStore
  server verifies bytes + SHA-256
        ↓
normalize_build(...)
        ↓
RuntimeInput
        ↓
BuildManager
        ↓
DryvRuntime.plan(...)
        ↓
GenerationPlan
        ↓
BuildSession PLAN_READY
```

Local filesystem paths are resolved by the Project Client before upload. The API receives logical resources and content, never the user's project root.

## Resource ownership

`resources/store.py` now owns build-scoped V1 resource storage and independently computes SHA-256 for every upload. Claimed-hash mismatches, conflicting IDs and oversize resources are rejected before Runtime invocation.

`resources/bundle.py` normalizes the uploaded pack-relative path map into `RuntimePack`/`RuntimePackResource` without interpreting the pack manifest. The build-scoped store remains attached to the normalized build so later renderer execution can retrieve exact template bytes referenced by the Runtime plan.

## Build lifecycle

`BuildSession` owns one isolated build status, `GenerationPlan`, diagnostics, cancellation state and ordered event history.

`BuildManager` owns create/get/run/cancel/release for sessions and holds one reusable `DryvRuntime`. Runtime events are forwarded into API events without changing their stage/message/details.

The API does not derive selectors, jobs, contexts, dependencies or artifact paths.

## Composition root

`DryvApiServer` exposes small build operations:

```text
accept_build
plan_build
submit_build
build
cancel_build
release_build
```

It delegates to `BuildManager` and contains no Canonical IR or pack semantics.

## Completion evidence

Completed on `develop` without test changes.

- request contracts represent only logical config/IR/resources/pack bundles;
- server verifies uploaded hashes rather than trusting client claims;
- normalized resources become the Engine's public `RuntimeInput` directly;
- `DryvRuntime.plan()` is the sole planning/semantic authority;
- Runtime progress becomes ordered API build events;
- completed plans remain available in the isolated `BuildSession` for renderer prerequisite work;
- there is no user project filesystem access or apply state in API/Runtime input;
- production files remain below the 500-line ceiling by inspection;
- no tests were added, modified or deleted.

Task 02 may now define the external Render Client protocol and preflight contract.
