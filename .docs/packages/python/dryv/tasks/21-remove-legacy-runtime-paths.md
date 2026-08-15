# Task 21 — Remove legacy runtime/plugin/port/write paths

Status: [ ]
Owner: `packages/python/dryv`
Depends on: Task 20 and replacement external Project Client/API path proven
Validation: no legacy imports, architecture tests, full Dryv suite

## Goal

After the feature-based Runtime works end to end, remove obsolete implementation paths that conflict with the approved architecture. Do not delete them earlier while they are still needed for migration safety.

## Remove or migrate obsolete responsibilities

Current code includes legacy areas such as:

```text
dryv/runtime/plugins.py
dryv/ports/source.py
dryv/ports/target.py
dryv/ports/templates.py
dryv/ports/writers.py
dryv/application/write.py
dryv/infrastructure/writers.py
```

This task must remove the obsolete ownership represented by those paths once no production code depends on it.

Also inventory and retire other old runtime/application/infrastructure modules whose only purpose was:

- in-engine template-engine registration/execution;
- generic target/source/writer abstraction superseded by explicit Features/resources/sessions;
- direct user-project output mutation;
- old generation/session composition superseded by `DryvRuntime` + Features.

## Required post-cleanup architecture

`packages/python/dryv` must contain no production path that:

- discovers template engines as in-process plugins;
- performs generated project file writes/deletes;
- exposes old generic writer/target abstractions as the main generation contract;
- bypasses Feature public facades for runtime coordination;
- imports obsolete compatibility semantic models after their migration window closes.

Compatibility re-exports that remain for a documented public API migration must be minimal, deprecated and point to the canonical implementation. No duplicated logic.

## Documentation cleanup

Update canonical Dryv docs and package README to describe only the active feature/runtime/session/artifact-stream architecture. Archive completed task material according to repository task rules after implementation is accepted.

## Non-goals

- Do not remove unrelated frozen/archive content.
- Do not rewrite working external packages in this task.
- Do not add new architecture while cleaning up.

## Allowed paths

- `packages/python/dryv/src/dryv/**`
- `packages/python/dryv/tests/**`
- `.docs/packages/python/dryv/**`

## Acceptance criteria

- no production imports of removed legacy paths remain;
- engine-side user-project writers are gone;
- old plugin discovery is gone;
- Runtime/Features are the only active generation orchestration path;
- full Dryv tests and architecture tests pass without broad exceptions.

## Validation

Search for imports/references to every removed module, run the full Dryv suite and architecture tests, run static typing/lint checks used by the package, and `git diff --check`. Record the removed paths and any deliberately retained compatibility surface.
