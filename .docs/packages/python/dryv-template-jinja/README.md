# dryv-template-jinja

Code: `packages/python/dryv-template-jinja`

Status: active implementation awaiting the approved standalone Render Client refactor beginning at [`tasks/00-standalone-render-client.md`](tasks/00-standalone-render-client.md).

This package is the Python/Jinja implementation of the shared Dryv Render Client protocol. Its target responsibility is intentionally small:

```text
template content + canonical JSON context
→ Jinja render
→ logical generated output bytes + content hash + renderer fingerprint
```

It does not select IR concepts, build template context, decide project paths, plan dependencies, or write user-project files. It must not require Dryv Runtime internals.

The package will support a transport-independent core renderer plus HTTP service and outbound WebSocket registration modes through the shared Render protocol.

The governing architecture is documented in [`../dryv/`](../dryv/README.md).
