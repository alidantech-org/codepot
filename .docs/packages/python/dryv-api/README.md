# dryv-api

Code target: `packages/python/dryv-api`

Status: planned package. Implementation begins at [`tasks/00-bootstrap-runtime-api-host.md`](tasks/00-bootstrap-runtime-api-host.md) after Dryv Runtime composition is ready.

`dryv-api` is the HTTP/WebSocket network host around `DryvRuntime`. It owns transport, build sessions, resource upload/streaming, progress/artifact delivery, cancellation, and connected Author/Render session registration.

It must not reimplement Canonical IR meaning, pack planning, template context generation, caching, scheduling semantics, or project filesystem writes.

```text
Project Client / Author Backend / Render Client
        ↓ HTTP / WebSocket
      dryv-api
        ↓ public runtime/session contracts
      DryvRuntime
```

The package may be deployed locally or remotely. The Dryv Engine must never depend back on `dryv-api`.

The governing architecture is documented in [`../dryv/`](../dryv/README.md).
