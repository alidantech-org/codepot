# dryv-cli

Code: `packages/python/dryv-cli`

Status: active implementation awaiting the approved Project Client refactor beginning at [`tasks/00-project-resource-client.md`](tasks/00-project-resource-client.md).

`dryv-cli` is a local Project Client and terminal frontend for Dryv. It owns terminal UX, project/workspace resource collection, connection to `dryv-api`, streaming build presentation, and safe local application of Dryv Artifact/WriteInstruction results.

The target flow is:

```text
local project
→ collect dryv.yaml/resources/previous managed outputs
→ dryv-api over HTTP/WebSocket
→ receive progress/diagnostics/artifacts
→ verify expected local hashes
→ apply writes atomically
→ persist managed-output state
```

The CLI does not own Canonical IR meaning, pack selection, template context construction, generation planning, cache semantics, or render/author implementation logic. Local and remote Runtime modes must use the same API client path rather than a separate in-process generation path.

The governing architecture is documented in [`../dryv/`](../dryv/README.md).
