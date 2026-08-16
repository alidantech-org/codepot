# Dryv Project Client API v1

Wire version: `dryv.api/v1`

This protocol connects a Project Client to an outer Dryv API host. It is intentionally separate from Canonical Dryv IR, Author Session, and Render Session contracts.

## Ownership

The Project Client owns local resource acquisition and local project mutation. The API host owns transport/session registration and invokes Dryv Runtime. Runtime owns semantic validation/planning/render/artifact classification.

A build request contains only explicit logical data. It never contains an arbitrary server-side project root that Runtime may traverse.

## Build request

Required top-level fields:

```json
{
  "apiVersion": "dryv.api/v1",
  "buildId": "stable-build-id",
  "resources": [],
  "packs": [],
  "planningCandidates": [],
  "previousManagedOutputs": [],
  "projectSnapshot": []
}
```

Exactly one IR source is selected:

```text
precompiledIrResourceId
or
author { connectionId, request }
```

The in-process Runtime contract also supports a direct already-decoded Contract, but that form is not part of the external API wire.

### Resources

```json
{
  "resourceId": "resource://project/model.ir.json",
  "mediaType": "application/vnd.dryv.ir+json",
  "contentHash": "optional transport/content identity",
  "contentBase64": "..."
}
```

Pack manifest and template references must resolve to supplied Resource IDs. Runtime does not clone repositories or open arbitrary paths.

### Packs

A pack input contains:

- normalized `dryv.pack.yaml` document data;
- manifest Resource ID;
- explicit template Resource inventory;
- media type;
- required renderer capability;
- optional approved selection relationship.

### Planning candidates

The v1 migration contract carries explicit normalized Planning candidates. This preserves deterministic/inspectable planning while user-facing selector/grouping vocabulary remains intentionally constrained. Candidates contain invocation/template/semantic/output/context/dependency/trace facts; Runtime validates them against normalized packs before Planning accepts them.

### Project snapshot

For every path Runtime must classify, the Project Client supplies:

```json
{
  "path": "src/user.ts",
  "exists": true,
  "contentHash": "sha256:v1:artifact-content:..."
}
```

This is an observation, not filesystem authority. The client must recheck hashes again immediately before applying returned instructions.

### Previous managed outputs

```json
{
  "path": "src/user.ts",
  "contentHash": "sha256:v1:artifact-content:...",
  "ownershipId": "pack-id:selection",
  "artifactId": "artifact.user"
}
```

Runtime uses this plus the project snapshot to classify safe changes.

## Build response metadata

The first build event is:

```json
{
  "type": "build-result",
  "result": {
    "apiVersion": "dryv.api/v1",
    "buildId": "...",
    "status": "render_complete",
    "success": true,
    "renderComplete": true,
    "diagnostics": [],
    "trace": [],
    "cache": {},
    "artifacts": [],
    "writeInstructions": [],
    "nextManagedOutputs": []
  }
}
```

`artifacts` contains metadata/provenance/size/hash, not the complete file body.

## Artifact content stream

Artifact bytes follow independently in bounded events:

```json
{
  "type": "artifact-content",
  "artifactId": "artifact.user",
  "offset": 0,
  "contentBase64": "...",
  "final": false
}
```

The client validates contiguous offsets, expected total size, and final artifact content hash before any project mutation.

The stream ends with:

```json
{
  "type": "stream-complete",
  "buildId": "...",
  "renderComplete": true
}
```

## Write instructions

Kinds:

```text
create
update
unchanged
delete_managed
```

An update/delete includes `expectedPreviousHash`. The Project Client must compare this to the actual local file immediately before mutation. A mismatch is a local apply conflict, even if Runtime observed a matching hash earlier.

## Completion states

`renderComplete` belongs to Runtime/API.

`applyComplete` is deliberately absent from this protocol response. It can only be produced by the Project Client after staged content has been validated and project mutations plus managed-output state have committed successfully.

## Cache mode

Optional:

```text
use
refresh
off
```

This is independent of whether a client later applies the returned artifacts. `commitCache` can disable successful cache mutation for plan/dry-run workflows.

## Cancellation

The outer host maps `buildId` to a Runtime cancellation token. A transport may expose cancellation with any framing appropriate to that transport. The JSONL reference host accepts:

```json
{"type":"cancel","buildId":"..."}
```

Cancellation propagates into Scheduling and established Author/Render sessions. Cancelled builds must not commit pending cache state or report `render_complete`.

## Transport independence

The repository reference uses line-delimited JSON for process-level proofs. HTTP, WebSocket, RPC, browser message channels, or other transports may implement the same wire contract. None of those hosting choices belong inside `dryv`.
