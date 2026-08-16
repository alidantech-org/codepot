# Task 19 — Build the Artifacts Feature and write-instruction stream

Status: [x]
Owner: `packages/python/dryv`
Depends on: Tasks 14, 15, 16 and 18
Validation: artifact classification tests, managed-output safety tests

> Implementation is complete on `develop`. Executable certification is still pending because the connected repository environment exposes no checkout/test runner. See [`../PROGRESS-18-25.md`](../PROGRESS-18-25.md).

## Goal

Make generated artifacts and safe write instructions the final product of Dryv Engine. Dryv plans and classifies project changes but does not physically mutate the user's project filesystem.

## Canonical generated artifact

Define a runtime artifact record containing at minimum:

```text
artifact id
planned project-relative path
logical output id
content bytes/stream when rendered
content hash
semantic subject/provenance
pack/template invocation provenance
dependency facts
status
```

Paths are normalized project-relative paths. Absolute host paths must never be semantic artifact identity.

## Write instructions

Classify each planned artifact against the Project Client's supplied previous managed-output manifest:

```text
CREATE
UPDATE
UNCHANGED
DELETE_MANAGED
```

Mutation instructions must include safety facts such as:

```text
expected previous managed hash
new content hash when applicable
managed ownership id
normalized relative path
reason/provenance
```

The Project Client performs actual reads/writes/deletes and verifies the expected old hash before mutation.

## Managed-output manifest

Define the engine-facing contract for previous managed outputs supplied by the Project Client. It must be sufficient to:

- detect unchanged outputs;
- identify stale outputs from earlier Dryv builds;
- refuse to classify an arbitrary unowned path for deletion;
- detect when a previously managed file was modified by the user since the recorded hash.

Dryv emits the next managed-output state as part of the build result; the Project Client persists it only after a successful local apply.

## Artifact delivery

Support bounded streaming of artifact metadata and content to the outer API/client layer. Large files must not require one giant JSON message.

Separate runtime states:

```text
render_complete
```

means all requested generated content was successfully produced.

`apply_complete` belongs to the Project Client/API acknowledgement flow and must not be faked by Dryv Engine.

## Dry-run/plan

Dry-run/plan produces the same planned artifact/write-instruction classification where possible but no project mutation occurs because the engine never performs project mutation anyway. Cache mutation rules remain controlled by Cache Feature/build mode.

## Non-goals

- Do not call filesystem APIs for user-project mutation.
- Do not perform atomic renames/deletes locally.
- Do not make renderer clients choose arbitrary output paths.

## Allowed paths

- `packages/python/dryv/src/dryv/features/artifacts/**`
- current ownership/write-planning models being migrated only where they represent engine-side artifact facts
- corresponding tests/docs/specs

## Acceptance criteria

- Dryv output is an artifact/write-instruction stream, not direct filesystem effects.
- create/update/unchanged/stale-managed classification is deterministic.
- delete instructions can target only previously managed outputs.
- user-modified previous managed files are detectable through expected hashes.
- next managed-output state is emitted but not persisted into the user's project by Dryv.

## Validation

Test first build, unchanged rebuild, changed content, stale managed output, user-modified managed output, collision/path traversal refusal, large streamed artifact and dry-run classification. Run architecture tests and `git diff --check`.
