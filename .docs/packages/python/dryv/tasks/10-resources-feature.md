# Task 10 — Build the Resources Feature

Status: [x]
Owner: `packages/python/dryv`
Depends on: Task 09
Validation: resource identity/streaming tests, architecture tests

> Implementation is complete on `develop`. External executable certification is still pending because the connected environment exposes no repository checkout or CI runner. See [`../PROGRESS-00-10.md`](../PROGRESS-00-10.md).

## Goal

Introduce `features/resources` so Dryv Engine operates on logical resources rather than assuming direct access to a user's project filesystem.

This is required for identical local and remote execution.

## Resource model

A resource must have a portable identity and bounded metadata such as:

```text
logical resource id
media type
size when known
content hash when known
bytes or readable stream
origin/provenance metadata where safe
```

Example logical identities:

```text
resource://project/dryv.yaml
resource://ir/main.jsonl
resource://pack/backend/dryv.pack.yaml
resource://pack/backend/templates/entity.ts.hbs
```

Logical resource IDs must not expose host-specific absolute paths as semantic identity.

## Responsibilities

The Feature should support:

- registering supplied resources;
- looking them up by logical ID or content hash;
- bounded streaming reads;
- immutable/content-addressed resource reuse;
- resource manifests describing what a build requires or already supplies;
- detecting conflicting resource IDs/hashes;
- normalizing path-like pack/project relative resource names safely.

## Project-client boundary

The Project Client is responsible for acquiring local files and private repository resources and supplying them to Dryv/API. Dryv Engine must not run Git or assume access to user credentials.

For remote builds, resource manifests should allow an API host to request only missing content-addressed blobs instead of requiring full retransmission every build.

## Non-goals

- Do not implement HTTP upload endpoints here.
- Do not implement filesystem reads from arbitrary project paths.
- Do not interpret IR or pack semantics.
- Do not perform artifact output writes.

## Allowed paths

- `packages/python/dryv/src/dryv/features/resources/**`
- existing resource/archive/source infrastructure being migrated only where owned by this capability
- corresponding tests/docs

## Acceptance criteria

- Engine features can consume logical resources without knowing host filesystem paths.
- resource streams are bounded and reusable through content hashes.
- conflicting logical IDs/content hashes fail clearly.
- private project acquisition remains outside Dryv Engine.

## Validation

Test in-memory resources, streamed resources, duplicate identical resources, conflicting resources, content-addressed lookup, normalized resource IDs and large bounded reads. Run architecture tests and `git diff --check`.
