# Task 02 — Add safe local artifact application and managed-output state

Status: [ ]
Owner: `packages/python/dryv-cli`
Depends on: Tasks 00–01 and Dryv Artifacts Feature
Validation: atomic write/delete safety tests, hash-conflict tests, API acknowledgement integration

## Goal

Make the CLI the local filesystem authority for generated project changes. It consumes Dryv Artifact/WriteInstruction streams, verifies current local state, applies safe changes atomically, and persists managed-output state only after successful application.

## Local filesystem feature

Organize local effects as an independently maintainable CLI/Project Client capability, for example:

```text
dryv_cli/features/filesystem/
```

It owns:

- safe project-relative path resolution;
- directory creation;
- file hashing;
- atomic temp-write + replace;
- managed deletion;
- platform-safe path normalization;
- permission/locking diagnostics.

It must not know IR, packs, template context or semantic planning.

## Apply rules

### CREATE

- refuse unsafe/out-of-root path;
- refuse unmanaged overwrite unless build instruction explicitly allows a reviewed force policy;
- write atomically;
- verify resulting content hash.

### UPDATE

- calculate current file hash;
- require it to equal `expected previous managed hash` before automatic replacement;
- on mismatch, report local modification conflict and do not overwrite by default;
- apply atomically when safe.

### UNCHANGED

- no write;
- optionally verify local managed file still matches expected hash before reporting successful apply.

### DELETE_MANAGED

- target must exist in previous managed-output state;
- current hash must match expected managed hash before automatic deletion;
- never broad-delete directories or glob unknown files.

## Managed-output manifest

Persist a project-local managed-output manifest containing stable artifact/path/hash/ownership facts required by the next build.

Update it only after all required local apply operations have succeeded. On partial failure, retain enough prior state/recovery information that the next run cannot treat unapplied outputs as successfully managed.

## API acknowledgement

Report per-artifact and terminal apply results back through `dryv-api`:

```text
applied
unchanged verified
refused/local conflict
apply failed
apply complete
```

Do not alter Runtime semantic diagnostics.

## Dry-run

Dry-run/plan must not mutate project files or managed-output state. It may present the received write instructions/diffs.

## Non-goals

- Do not plan artifact paths locally.
- Do not decide stale outputs independently from Dryv instructions.
- Do not calculate template/IR cache semantics.

## Allowed paths

- `packages/python/dryv-cli/**`
- `.docs/packages/python/dryv-cli/**`

## Acceptance criteria

- first build safely creates files.
- unchanged rebuild does no write.
- expected-hash update is atomic.
- user-modified managed file is never silently overwritten/deleted.
- stale managed file deletion is conservative.
- managed-output manifest is committed only after successful apply.
- API receives accurate apply acknowledgements.

## Validation

Test create/update/unchanged/delete-managed, path traversal, unmanaged collision, user modification, partial failure, dry-run, atomic replacement and API apply acknowledgement. Run CLI tests and `git diff --check`.
