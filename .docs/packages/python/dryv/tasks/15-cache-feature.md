# Task 15 — Build the Cache Feature

Status: [x]
Owner: `packages/python/dryv`
Depends on: Tasks 11 and 14
Validation: cache-key tests, invalidation tests, deterministic replay tests

> Implementation is complete on `develop`. External executable certification is still pending because the connected environment exposes no repository checkout or CI runner. See [`../PROGRESS-11-17.md`](../PROGRESS-11-17.md).

## Goal

Create `features/cache` as the single owner of build-cache records and cache policy. Cache must avoid stale code by keying on canonical semantic dependencies, context, templates, renderer identity and relevant options.

## Cache stages

Support at least three independent stages:

### 1. Context cache

Key from:

```text
relevant IR record/branch hashes
context projection contract/version
pack declaration hash
project bindings/options used by the context
```

A hit avoids rebuilding the canonical JSON context.

### 2. Render cache

Key from:

```text
context hash
template hash
renderer fingerprint
render options affecting output
render protocol/context version
```

A hit avoids calling a Render Client.

### 3. Artifact comparison metadata

Track generated content hashes and prior managed-output facts needed to classify artifact instructions. Physical project-file comparison/application remains outside Dryv Engine.

## Cache modes

Implement explicit modes:

```text
use      # normal read/write cache behavior
refresh  # ignore reusable entries, recompute, then update cache
 off     # no cache read/write
```

Cache mode must be independent from build side-effect mode. A dry-run/plan can request fresh computation without committing cache mutations if the project/build contract says so.

## Storage abstraction

The Feature may own engine-local cache persistence, but persistence must be replaceable and deterministic. Cache storage is engine infrastructure, not user-project output ownership.

Cache entries must be versioned and include enough metadata to reject incompatible records after protocol/context changes.

## Safety

- never reuse a render result with a different renderer fingerprint;
- never key only on template path or source timestamps;
- never let an unrelated IR change invalidate all outputs when Planning reports narrower dependencies;
- never commit incomplete/failed build cache state as successful;
- cancellation/failure must leave prior valid entries usable.

## Non-goals

- Do not write generated project files.
- Do not decide semantic dependency sets; Planning/IR provide them.
- Do not calculate hash algorithms independently; Hashing Feature owns hashes.

## Allowed paths

- `packages/python/dryv/src/dryv/features/cache/**`
- existing cache modules being migrated where owned by this capability
- corresponding tests/docs

## Acceptance criteria

- context and render cache keys are explicit/versioned and reproducible.
- renderer changes invalidate render cache.
- relevant nested semantic changes invalidate dependent contexts/renders.
- unrelated semantic changes preserve cache hits.
- refresh/off/use modes behave independently of dry-run/render modes.
- failed/cancelled builds cannot poison cache state.

## Validation

Add tests for stable hits, template changes, renderer-version changes, relevant/unrelated IR changes, pack-option changes, refresh/off behavior, failure rollback and deterministic cache serialization. Run architecture tests and `git diff --check`.
