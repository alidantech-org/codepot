# Task 08 — Build the Serialization Feature

Status: [x]
Owner: `packages/python/dryv`
Depends on: Task 07
Validation: canonical round-trip tests, JSONL streaming tests, architecture tests

> Implementation is complete on `develop`. External executable certification is still pending because the connected environment exposes no repository checkout or CI runner. See [`../PROGRESS-00-10.md`](../PROGRESS-00-10.md).

## Goal

Move JSON, YAML and JSONL mechanics behind one independent `features/serialization` capability. These are representations of one Canonical Dryv IR, not separate semantic models.

## Public responsibility

The Feature must support deterministic operations equivalent to:

```text
decode resource bytes → representation records
decode JSON/YAML document → canonical records
decode JSONL stream → canonical records
encode canonical records → JSON
encode canonical records → YAML
encode canonical records → JSONL
```

Runtime/IR validation remains responsible for deciding whether decoded records are valid Dryv meaning.

## JSONL

JSONL is a first-class scalable transport:

- support record-by-record streaming;
- avoid requiring the entire IR in memory;
- preserve stable record identity;
- support byte offset/length indexing where useful for later lazy lookup;
- permit deterministic per-record hashes without reserializing with different canonicalization rules.

## Canonical encoding

Define one canonical JSON-compatible representation used for hashing/protocol boundaries. Equivalent IR meaning loaded from JSON/YAML must normalize to the same canonical structure and hashes.

Preserve version fields required to reject unsupported IR versions.

## Feature boundary

Serialization knows bytes, media types, representation versions and canonical portable values. It does not know:

- template packs;
- renderer sessions;
- project output paths;
- filesystem writes;
- author language implementations;
- build scheduling.

## Non-goals

- Do not implement semantic reference resolution here.
- Do not load `dryv.yaml` or `dryv.pack.yaml` semantics here; Project/Packs Features own those meanings while using Serialization mechanics.
- Do not add project filesystem access.

## Allowed paths

- `packages/python/dryv/src/dryv/features/serialization/**`
- existing IR codec modules being migrated
- corresponding tests/docs

## Acceptance criteria

- Runtime can parse/emit supported IR representations only through the Feature public API.
- JSONL is streamable and bounded.
- semantic-equivalent JSON/YAML normalize identically.
- malformed syntax and unsupported representation versions produce structured diagnostics.
- no semantic/generation logic leaks into Serialization.

## Validation

Test JSON, YAML and JSONL round trips; large JSONL bounded iteration; malformed records; version rejection; canonical ordering; equivalent representation normalization. Run architecture tests and `git diff --check`.
