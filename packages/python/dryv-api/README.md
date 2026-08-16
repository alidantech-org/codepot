# dryv-api

`dryv-api` is the outer host around the transport-neutral `dryv` Runtime. It owns versioned client wire decoding, established Author/Render connection registration, build cancellation handles, and streamed artifact delivery. It does not redefine Canonical IR, pack meaning, planning, caching, or rendering semantics.

## Ownership

```text
Project Client ── dryv.api/v1 ──> dryv-api
                                |
                                +--> DryvRuntime
                                +--> established Author Sessions
                                +--> established Render Sessions
```

The Runtime never hosts HTTP/WebSocket itself. `dryv-api` may expose stdio, HTTP, WebSocket, RPC, or another transport while keeping the same engine contract.

## JSONL host

The repository includes a process-isolated host:

```bash
python -m dryv_api.stdio
```

The host supports `hello`, `build`, `cancel`, and `shutdown` messages. Builds run independently of the stdin reader so cancellation can arrive while work is active.

Renderer process connections are configured outside Runtime with `DRYV_RENDER_CONNECTIONS_JSON`; Author Backend commands use `DRYV_AUTHOR_CONNECTIONS_JSON`. Runtime receives already-established sessions only.

## Build result and artifact stream

The first build event contains metadata:

- status / `renderComplete`;
- diagnostics and trace;
- context/render cache hit/miss counts;
- artifact IDs, paths, hashes, provenance, and sizes;
- `CREATE`, `UPDATE`, `UNCHANGED`, or `DELETE_MANAGED` instructions;
- the next managed-output manifest.

Artifact bytes follow in bounded `artifact-content` events. `dryv-api` never reports `applyComplete`; only the Project Client can know whether local project mutation succeeded.

## Process transports

`SubprocessRenderSession` and `SubprocessAuthorSession` adapt independent JSONL processes into established Runtime sessions. This proves renderers and author backends can live in different languages/processes without becoming Dryv plugins.

## Validation

```bash
uv run --all-packages pytest packages/python/dryv-api/tests
uv run --all-packages ruff check packages/python/dryv-api
```
