# Task 00 — Rebuild the final dryv-api structure

Status: [x]
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

## Ownership

`server.py` is the API composition root only. It may wire Runtime, BuildManager, ResourceStore, RendererRegistry, scheduler and delivery services. It must not contain pack/IR semantics.

`contracts.py` contains only public API transport/build contracts. It must not duplicate Runtime semantic contracts.

## Completion evidence

Completed on `develop` without test changes.

- The production package now has exactly the approved root ownership directories/files.
- `service.py`, `stdio.py`, `subprocess_author.py`, and `subprocess_render.py` were physically removed.
- Old AuthorSession/RenderSession/stdin/subprocess contracts were not preserved through alternate modules.
- Renderer/build/resource/delivery/transport modules are separated by the approved ownership tree.
- No project filesystem writer exists.
- No new production file approaches the 500-line ceiling.
- No tests were added, modified or deleted.

Task 01 may now implement real build input normalization and Runtime coordination inside this structure.
