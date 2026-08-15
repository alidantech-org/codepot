# dryv-render-handlebars

Code target: `packages/nodejs/dryv-render-handlebars`

Status: planned package. Implementation begins at [`tasks/00-standalone-render-client.md`](tasks/00-standalone-render-client.md).

This package is the Node.js/Handlebars implementation of the shared Dryv Render Client protocol.

Its responsibility is intentionally limited:

```text
template content + canonical JSON context
→ Handlebars render
→ logical generated output bytes + content hash + renderer fingerprint
```

It does not understand Canonical Dryv IR semantics, select templates, build context, plan artifact paths/dependencies, or write project files.

The package will provide a transport-independent core renderer plus HTTP service and outbound WebSocket registration modes.

See the canonical Dryv architecture under `.docs/packages/python/dryv/`.
