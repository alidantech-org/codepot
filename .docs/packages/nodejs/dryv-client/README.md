# dryv-client

Code target: `packages/nodejs/dryv-client`

Status: planned TypeScript client package. Implementation begins at [`tasks/00-http-ws-api-client.md`](tasks/00-http-ws-api-client.md).

`dryv-client` is the shared TypeScript HTTP/WebSocket client for browser, VS Code, desktop and other JavaScript frontends that talk to `dryv-api`.

The core package owns transport/protocol concerns only: build creation, resource negotiation/upload, progress/diagnostic streams, artifact streaming, cancellation, reconnect and apply acknowledgements.

A Node-only project layer adds trusted local resource collection and safe Artifact/WriteInstruction application for VS Code/desktop-style clients. Browser builds must remain free of Node filesystem/process dependencies.

The package never imports Dryv Engine or duplicates IR/pack/planning semantics.

See the canonical Dryv architecture under `.docs/packages/python/dryv/`.
