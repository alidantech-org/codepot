# Handlebars Render Client

This module is a reference independent Render Client for the Dryv Render Session protocol. It is hosted under the existing `codepotx` workspace only so the repository can reuse its already-locked Handlebars 4.7.9 dependency without changing `pnpm-lock.yaml` during the Dryv architecture migration.

It does **not** import Codepot/Dryv generation code or Runtime internals.

## Run

```bash
node packages/nodejs/codepotx/render-clients/handlebars/stdio.mjs
```

The process speaks line-delimited JSON and supports:

- `hello`
- `render`
- `cancel`
- `shutdown`

It advertises capability `handlebars/v1`, render/context protocol version 1, supported Handlebars media types, deterministic output, and a renderer fingerprint. `DRYV_RENDERER_REVISION` participates in that fingerprint so Task-23 integration tests can prove renderer identity changes invalidate only the relevant render cache entries.

The process receives only template bytes, canonical JSON context, logical output declarations, and render options. It does not receive Canonical IR objects or project filesystem access.
