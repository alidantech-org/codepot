# Task 00 — Rebuild the final dryv-api structure

Status: [ ]
Owner: `packages/python/dryv-api`
Depends on: Dryv Task 27

## Goal

Remove the superseded stdio/subprocess/session-host architecture and reshape `dryv-api` to the approved build/resource/renderer/delivery/transport ownership tree.

Do not preserve old API behavior through compatibility modules.

## Required production tree

```text
dryv_api/
├── __init__.py
├── py.typed
├── server.py
├── contracts.py
├── builds/
│   ├── __init__.py
│   ├── session.py
│   ├── manager.py
│   └── events.py
├── resources/
│   ├── __init__.py
│   ├── bundle.py
│   └── store.py
├── renderers/
│   ├── __init__.py
│   ├── protocol.py
│   ├── connection.py
│   ├── registry.py
│   ├── preflight.py
│   └── scheduler.py
├── delivery/
│   ├── __init__.py
│   ├── streaming.py
│   ├── bundle.py
│   └── manifest.py
└── transport/
    ├── __init__.py
    ├── http.py
    └── websocket.py
```

## Required removals

Delete rather than shim:

```text
dryv_api/service.py
dryv_api/stdio.py
dryv_api/subprocess_author.py
dryv_api/subprocess_render.py
```

Remove old contracts for:

- AuthorSession/Author Backend registration;
- Runtime RenderSession injection;
- `planningCandidates` wire input;
- `renderSessionIds` wire input;
- previous managed-output/project snapshot data passed into Runtime;
- stdio/subprocess-first hosting.

## Ownership

`server.py` is the API composition root only. It may wire Runtime, BuildManager, ResourceStore, RendererRegistry, scheduler and delivery services. It must not contain pack/IR semantics.

`contracts.py` contains only public API transport/build contracts. Do not duplicate Runtime semantic contracts.

## Code-size enforcement

Every production file must remain at or below 500 lines. Do not create alternate `services`, `controllers`, `utils`, `helpers`, `common`, `shared`, `legacy` or adapter trees.

## No-test gate

Do not create, modify or rewrite tests. Existing tests do not justify preserving superseded API contracts.

## Allowed paths

- `packages/python/dryv-api/**`
- `.docs/packages/python/dryv-api/**` for factual task status/progress

## Completion evidence

Confirm by production-tree inspection that:

- only the approved API ownership tree remains;
- old subprocess/stdio/session compatibility files are gone;
- no API file reimplements Canonical IR, pack selection or context construction;
- no project filesystem writer exists;
- every production file is at or below 500 lines;
- no tests were added or modified.
