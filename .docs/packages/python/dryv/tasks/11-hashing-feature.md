# Task 11 — Build the Hashing Feature

Status: [x]
Owner: `packages/python/dryv`
Depends on: Task 10
Validation: deterministic hash tests, cross-representation tests

> Implementation is complete on `develop`. External executable certification is still pending because the connected environment exposes no repository checkout or CI runner. See [`../PROGRESS-11-17.md`](../PROGRESS-11-17.md).

## Goal

Centralize deterministic content and semantic hashing behind `features/hashing`. Hashes are used for resource reuse, IR change detection, context caching, render caching and artifact comparison.

## Required hash families

The Feature must support typed hash purposes rather than a single ambiguous helper:

```text
resource content hash
canonical document hash
canonical IR record hash
canonical IR branch/subtree hash
pack manifest hash
template content hash
context hash
renderer fingerprint hash
artifact content hash
build-input hash
```

Use one documented cryptographic hash algorithm/version for canonical identities unless an explicit protocol version says otherwise.

## Canonicalization

Hash inputs must be canonical bytes. Equivalent semantic content loaded from JSON and YAML must not hash differently merely because of formatting/key order.

For canonical IR:

- direct record hash covers the canonical record itself;
- branch/subtree hash incorporates only the declared semantic dependencies needed to represent that branch;
- dependency ordering is deterministic;
- cycles are detected and diagnosed rather than recursively hashing forever.

The IR Runtime Feature will provide the semantic dependency graph; Hashing performs the deterministic hash computation.

## Incremental behavior

Design APIs so one changed unrelated Schema does not invalidate all branch hashes. Hash computation should be cacheable and compositional.

For JSONL resources, allow a per-record hash to be computed from the same canonical bytes used for storage/transport.

## Non-goals

- Do not decide which IR dependencies are relevant to a template context; Planning owns that.
- Do not store caches here; Cache Feature owns persisted/in-memory cache entries.
- Do not compare/write user files.

## Allowed paths

- `packages/python/dryv/src/dryv/features/hashing/**`
- corresponding tests/docs

## Acceptance criteria

- every cache/provenance hash purpose has explicit typed API/identity;
- hash outputs are deterministic across processes/platforms;
- semantically equivalent canonical values hash the same;
- unrelated branch changes do not globally invalidate all branches;
- cycles/errors are structured diagnostics.

## Validation

Add golden-vector tests, JSON/YAML equivalence tests, JSONL record tests, branch dependency tests, unrelated-change tests and cycle tests. Run architecture tests and `git diff --check`.
