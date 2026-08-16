# Current work

Dryv Engine and `dryv-api` are being rebuilt to the approved server-generation architecture.

Mandatory references before implementation:

- [`packages/python/dryv/ARCHITECTURE.md`](packages/python/dryv/ARCHITECTURE.md)
- [`packages/python/dryv/IMPLEMENTATION-RULES.md`](packages/python/dryv/IMPLEMENTATION-RULES.md)

Implementation order:

1. [`Dryv Task 26 — Final Engine boundary cleanup`](packages/python/dryv/tasks/26-final-engine-boundary-cleanup.md)
2. [`Dryv Task 27 — Build the GenerationPlan Runtime`](packages/python/dryv/tasks/27-generation-plan-runtime.md)
3. [`dryv-api Task 00 — Rebuild the final API structure`](packages/python/dryv-api/tasks/00-final-api-structure.md)
4. [`dryv-api Task 01 — Build input and Runtime coordination`](packages/python/dryv-api/tasks/01-build-input-and-runtime-coordination.md)
5. [`dryv-api Task 02 — Render Client protocol and template preflight`](packages/python/dryv-api/tasks/02-render-client-protocol-and-preflight.md)
6. [`dryv-api Task 03 — Render scheduling and artifact streaming`](packages/python/dryv-api/tasks/03-render-scheduling-and-artifact-streaming.md)
7. [`dryv-api Task 04 — Bundle and HTTP/WebSocket delivery`](packages/python/dryv-api/tasks/04-bundle-and-http-websocket-delivery.md)

## Mandatory gate

Do not create, modify or rewrite tests during Tasks 26–27 or API Tasks 00–04. Do not preserve superseded production architecture to satisfy old tests.

After API Task 04, stop for explicit user review of the final production file/folder structure and code. Test implementation begins only after the user explicitly lifts this gate.

Deferred client work such as CLI, authoring implementations, Jinja/Handlebars clients, MCP adapters and TypeScript Project Clients is not part of the current implementation sequence.
