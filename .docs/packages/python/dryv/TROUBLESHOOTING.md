# Dryv troubleshooting

Troubleshoot by ownership boundary first. Dryv is intentionally split so a failure can be attributed to Project Client, API/session transport, Runtime Feature, Author Backend, Render Client, or local apply.

## Resource failures

Symptoms:

```text
missing precompiled IR resource
missing pack manifest resource
missing template resource
resource hash mismatch
unsupported media type
```

Check the Project Client/API build request Resource inventory. Every referenced IR/manifest/template must be supplied explicitly by logical `resource://` ID.

Do not fix this by giving Runtime an arbitrary host path.

## Canonical IR validation failures

Look for diagnostics from the IR Runtime Feature:

```text
duplicate semantic id
unknown typed reference
invalid ownership
Schema extension cycle/override error
invalid StorageMapping field/reference
Workflow/View/Presentation reference error
```

The Author Backend may successfully compile source while Runtime still rejects the resulting Canonical IR. Runtime validation is authoritative.

## Pack/planning failures

Typical causes:

```text
unknown pack id
unknown template resource
selection/template mismatch
unsafe output path
missing artifact dependency
artifact dependency cycle
non-JSON context value
non-finite context number
context size limit
```

Inspect the build trace and normalized Planning candidate. Do not add hidden fallback selection behavior; fix the explicit pack/planning declaration.

## Renderer capability mismatch

A planned invocation declares a renderer capability, e.g. `jinja/v1` or `handlebars/v1`.

If Scheduling reports no compatible worker/session:

- confirm the outer API host registered the expected connection;
- inspect its `hello` capabilities;
- confirm protocol/context versions and template media type;
- confirm pack template inventory requires the intended capability.

Runtime does not discover/install template engines.

## Renderer result rejection

Templating rejects:

```text
wrong job id
renderer fingerprint changes mid-job
unknown/duplicate/missing logical output id
unsupported protocol/context/media type
invalid output content hash
cancelled result
```

The Render Client must return only outputs planned by Runtime.

## Author Backend mismatch

Authoring rejects:

```text
unsupported protocol version
unsupported IR version
unsupported source kind
record streaming without advertised support
mixed document/record representations
wrong completion job id/fingerprint
invalid Canonical IR
```

Precompiled IR does not need an Author Session at all.

## Cache misses

Context cache identity depends on semantic dependency branch hashes, projection/context contract version, pack declaration identity and relevant input facts.

Render cache identity includes:

```text
context hash
template hash
renderer fingerprint
render options
render protocol version
context version
```

Expected invalidation examples:

- relevant IR branch change → dependent context/render miss;
- unrelated IR change → unrelated output remains reusable;
- template change → render miss for that template;
- renderer version/helper/fingerprint change → affected render miss;
- `refresh` → reusable entries intentionally ignored;
- `off` → no cache read/write.

A failed/cancelled build rolls back pending cache mutations. Prior valid cache entries remain usable.

## Artifact collision or user modification

`ARTIFACT_UNMANAGED_COLLISION`:

Runtime planned CREATE for a path the Project Client reported already exists without previous managed ownership. Dryv refuses to overwrite it.

`ARTIFACT_USER_MODIFIED` / `ARTIFACT_USER_MODIFIED_STALE`:

The observed local hash does not match the previous managed-output hash. Dryv refuses UPDATE/DELETE classification.

Do not update the managed-output manifest merely to silence the conflict. Decide whether to preserve/rename/reconcile the user's file.

## Client apply conflict after render_complete

`CLIENT_APPLY_CONFLICT` means the local file changed **after** the snapshot used by Runtime but before local mutation.

This is expected optimistic-concurrency protection:

```text
Runtime render_complete
        ↓
local file changes
        ↓
Project Client rechecks expectedPreviousHash
        ↓
apply refused
```

The Runtime build may still legitimately be `render_complete`; `apply_complete` is false/absent.

## Artifact stream failures

Project Client checks:

```text
build-result arrives before artifact content
offset is contiguous
artifact id was declared
base64 is valid
stream completes
received size matches metadata
content hash matches metadata
```

A partial/disconnected stream is never applied.

## Cancellation

The outer API host owns the build cancellation handle. Scheduling propagates cancellation to in-flight sessions and marks unresolved required jobs cancelled/blocked. Cache transaction is rolled back.

If a renderer process does not support prompt cooperative cancellation, the outer transport may terminate/reconnect it according to deployment policy; Runtime should still never report success for the cancelled build.

## `render_complete` but no local files changed

This can be correct. Check whether the Project Client actually invoked local apply. Runtime/API intentionally stop at artifact/write instructions.

For preview/web/download flows, no project mutation may occur by design.

## Workspace lock mismatch after migration

Tasks 18–25 added `packages/python/dryv-api` to the `packages/python/*` uv workspace and removed old Dryv dependencies from `dryv-cli` and `dryv-template-jinja`.

The repository-editing environment could not run uv, so regenerate and commit the lock from a real checkout:

```bash
uv lock
uv lock --check
```

Do not manually fabricate package resolution records.

## Certification commands

```bash
uv lock
uv run --all-packages pytest
uv run --all-packages ruff check packages/python/dryv packages/python/dryv-api packages/python/dryv-author packages/python/dryv-cli packages/python/dryv-template-jinja
pnpm install --frozen-lockfile
git diff --check
```

If a check fails, fix the owning boundary/Feature first. Do not reintroduce the removed plugin/port/writer architecture as a compatibility shortcut.
