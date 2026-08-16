# Dryv deployment and usage flows

Dryv Engine is transport-neutral. Deployment changes where the Project Client, API host, Author Backend and Render Clients run; it does not change Canonical IR or pack semantics.

## 1. Local CLI + local API + local Jinja

```text
CLI Project Client
    ↓ JSONL dryv.api/v1
python -m dryv_api.stdio
    ↓ Render Session
python -m dryv_template_jinja.stdio
```

The CLI owns the project root. The API/Runtime receives only logical resources and project-relative hash observations.

Reference CLI command:

```bash
dryv build request.json --root .
```

The default API command is:

```bash
python -m dryv_api.stdio
```

Renderer connection processes are configured by the outer host, not Runtime.

## 2. Local Project Client + remote API

A different transport may send the same `dryv.api/v1` request to a remote service:

```text
local Project Client
    ↓ HTTPS/WebSocket/RPC
remote dryv-api
    ↓
remote Dryv Runtime
```

The local root is never sent. Explicit source/pack resource bytes may be uploaded as Resources. Returned artifacts are hash-verified and applied locally.

The Task-24 JSONL multi-process fixture proves this ownership without requiring internet/cloud infrastructure.

## 3. Remote API + outbound/local Render Client

The outer API host can register an already-established Render Session whose process/service lives elsewhere:

```text
remote Runtime
    ↓ established Render Session
local/private renderer process
```

Only template bytes, canonical JSON context, logical outputs, render options and hashes cross the Render protocol. The renderer does not need project filesystem access.

Reference clients:

```bash
python -m dryv_template_jinja.stdio
node packages/nodejs/codepotx/render-clients/handlebars/stdio.mjs
```

## 4. Precompiled Canonical IR

A Project Client can upload:

```text
resource://project/model.ir.json
resource://project/model.ir.yaml
resource://project/model.ir.jsonl
```

and set `precompiledIrResourceId`. Runtime bypasses Authoring entirely and loads/validates the IR through Serialization + IR Runtime.

## 5. Python Author Backend

When the project uses authored Python source instead of precompiled IR:

```text
Project Client uploads logical Python source
    ↓
dryv-api selects established python Author connection
    ↓
python -m dryv_author.stdio
    ↓ Canonical IR
Runtime validation/planning
```

The author source may expose:

```python
def build_author() -> Author:
    ...
```

or `AUTHOR`.

The Author Backend knows no packs, output paths, Render Clients or local project root.

## 6. Web/playground preview/download

A browser Project Client may use the same API contract:

```text
browser resources/editor state
    ↓ dryv.api/v1
API/Runtime
    ↓ artifact stream
browser preview/download
```

The browser can choose not to persist/apply anything. `render_complete` is enough for preview/download. Cache commit policy can be disabled for a plan/preview request using `commitCache: false`.

## 7. VS Code / Node Project Client

`packages/nodejs/dryv-client/src/index.ts` defines the transport-neutral TypeScript API contract for editors/desktop/web/agent hosts.

The source is intentionally not yet an active pnpm workspace package because the migration environment could not regenerate `pnpm-lock.yaml`. Promote it only together with a real `pnpm install` lock update.

A VS Code extension should:

- collect explicit workspace resources locally;
- compute local observed hashes;
- call a `DryvTransport` implementation;
- validate streamed artifact hashes;
- apply edits through VS Code workspace APIs;
- persist managed-output state only after successful apply.

It must not import or run Dryv Runtime directly.

## 8. Cache modes

`use`:

```text
reuse compatible context/render cache entries; write successful new entries
```

`refresh`:

```text
ignore reusable entries; recompute; replace cache only after success
```

`off`:

```text
no cache reads/writes
```

Cache mode is independent from local apply. A Project Client can request a build, inspect the plan/artifacts, and decline local mutation.

## 9. Plan/dry-run

The engine architecture has no direct filesystem side effects, so planning/rendering is naturally separable from apply.

For a non-mutating client workflow:

```text
commitCache: false
receive render_complete/artifacts/writeInstructions
inspect/preview
do not call local apply
```

Future API endpoints may expose earlier planning-only results without changing ownership.

## 10. Cancellation/failure/reconnect

The outer host maps `buildId` to a Runtime cancellation token. Scheduling propagates cancellation to established sessions. Failed/cancelled builds roll back pending cache state.

Transport failure can only be retried automatically when explicitly classified retry-safe. A renderer semantic/template error is terminal for that job/build dependency path.

If a Project Client disconnects after `render_complete`, Runtime still must not claim `apply_complete`. The client may reconnect/rebuild, compare its persisted managed-output state, request fresh artifact content, and apply only after local hash revalidation.

## 11. Local apply safety

Immediately before UPDATE/DELETE, the client checks:

```text
actual local file hash == expectedPreviousHash
```

If not, apply fails locally even if Runtime observed a matching snapshot earlier. CREATE refuses an existing unmanaged path. Local commit stages content and rolls back partial mutations on failure.

## Reference integration fixtures

```text
packages/python/dryv-api/tests/integration/test_reference_pack.py
packages/python/dryv-api/tests/integration/test_multi_renderer_cache.py
packages/python/dryv-api/tests/integration/test_remote_runtime_local_project.py
```

These are the executable proof definitions for Tasks 22–24.
