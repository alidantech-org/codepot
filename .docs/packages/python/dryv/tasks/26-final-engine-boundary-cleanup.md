# Task 26 — Final Engine boundary cleanup

Status: [x]
Owner: `packages/python/dryv`
Depends on: approved `ARCHITECTURE.md` and `IMPLEMENTATION-RULES.md`

## Goal

Remove the superseded execution architecture from Dryv Engine and make the production package tree match the approved semantic/planning-only Engine boundary.

This is deletion and ownership cleanup first. Do not preserve old entry points through aliases, facades, adapters or deprecation shims.

## Required result

Dryv Engine owns only:

```text
ir
features/
    serialization
    project
    resources
    hashing
    ir
    packs
    planning
    cache
    diagnostics
runtime/
versions
```

Runtime must no longer own author execution, renderer sessions, renderer capacity/scheduling, generated artifact bytes, bundle creation or project filesystem logic.

## Required runtime tree

```text
dryv/runtime/
├── __init__.py
├── contracts.py
├── events.py
└── runtime.py
```

Remove the old `runtime/engine.py` and `runtime/facade.py`; do not make them forwarding modules.

## Required removals

Remove superseded production owners including:

```text
dryv/api/
dryv/config/
dryv/domain/
dryv/testing/
dryv/features/authoring/
dryv/features/templating/
dryv/features/scheduling/
dryv/features/artifacts/
```

Also audit any remaining top-level package. If it only duplicates/re-exports an approved owner, remove it.

Remove old Runtime contracts/concepts for:

- AuthorSession/Author Backend execution;
- AvailableRenderSession/RenderSession;
- renderer fingerprints/capacity as Runtime connection state;
- network/distributed render workers;
- generated artifact byte ownership;
- managed-output/local project snapshots;
- Runtime write instructions;
- stdio/subprocess execution assumptions.

Do not re-home those concepts under new names inside `dryv`.

## Preserve

Preserve canonical IR semantics and the already valid deterministic feature work that belongs to the approved Feature set. Refactor only where needed to remove forbidden ownership or to fit the final small-file tree.

## Code-size enforcement

- Every production source file must remain at or below 500 lines.
- Split by named architectural responsibility before reaching the limit.
- Do not create generic `utils`, `helpers`, `common`, `shared`, `misc`, `services`, or compatibility directories to make files smaller.

## No-test gate

Do not create, modify or rewrite tests in this task.

Existing tests that require removed architecture do not justify compatibility code. Test redesign is deferred until the user approves the final production code.

## Allowed paths

- `packages/python/dryv/**`
- `.docs/packages/python/dryv/**` only for factual progress/status corrections

## Completion evidence

Completed on `develop` without touching tests.

- The production root is now only `features`, `ir`, `runtime`, `versions`, `__init__.py`, and `py.typed`.
- The Feature catalog is exactly serialization, project, resources, hashing, ir, packs, planning, cache, diagnostics.
- `runtime/` contains only `__init__.py`, `contracts.py`, `events.py`, and `runtime.py`.
- Authoring, Templating, Scheduling, Artifacts, old inner API/config/domain/testing owners, Runtime engine/facade, and canonical IR re-export compatibility shims were removed rather than forwarded.
- Canonical diagnostic primitives moved under `dryv.ir.diagnostics`; retained IR code points directly at that owner.
- Runtime contracts no longer contain AuthorSession, RenderSession, renderer capacity, generated-byte, managed-output, filesystem-write, stdio, or subprocess concepts.
- Production source files introduced/rewritten by this task are below the 500-line limit.
- No tests were added, changed, deleted, or used as a reason to restore compatibility code.

Task 27 may now implement the complete GenerationPlan flow on this clean boundary.
