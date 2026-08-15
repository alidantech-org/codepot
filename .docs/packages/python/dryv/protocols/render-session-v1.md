# Dryv Render Session Protocol v1

## Purpose

This document is the language-neutral contract between Dryv Runtime and an established Render Session. Python classes under `dryv.features.templating` are one implementation of this contract; they are not the wire authority.

The protocol is transport-neutral. A session may be backed by local IPC, HTTP, WebSocket, another process boundary, or an in-memory test adapter. Dryv Engine does not host or choose that transport.

## Version

Protocol version: `1`

Template-context version is negotiated independently because a renderer may support several context contracts over one render protocol.

## Renderer hello

A renderer advertises:

```text
renderer id
renderer version
renderer fingerprint
renderer capabilities
supported render protocol versions
supported template-context versions
supported template media types
maximum concurrency/capacity
determinism declaration
```

The fingerprint MUST change whenever output-affecting renderer behavior changes, including output-affecting helpers/extensions.

## Render request

A request contains:

```text
protocol version
context version
stable job id
required renderer capability
template logical resource id
template media type
template content or established resource reference
template content hash
canonical JSON-compatible context
context hash
planned logical outputs
render options affecting output
```

Dryv Planning owns the allowed logical output identities and paths. Renderers do not choose arbitrary project destinations.

## Planned output

Each planned output contains:

```text
logical output id
planned project-relative path
```

One invocation normally has one output. Multi-output rendering is valid only when all returned outputs were declared in the request.

## Render result

A result contains:

```text
job id
renderer fingerprint
zero or more structured diagnostics
cancelled state
rendered logical outputs
```

Each rendered output contains:

```text
logical output id
content bytes/stream
content hash
```

## Validation rules

Dryv rejects a result when any of the following is true:

- required renderer capability is not advertised;
- protocol/context version is unsupported;
- template media type is unsupported;
- result job id differs from the request job id;
- renderer fingerprint changes during the job;
- an output id is duplicated;
- an output id was not planned;
- a planned output is missing;
- returned content does not match its declared content hash;
- a cancelled job returns as successful work.

## Diagnostics

Renderer diagnostics are structured records containing at minimum a stable code, message, and severity. Diagnostics are returned to Runtime unchanged in meaning; renderers do not redefine Dryv semantic diagnostics.

## Cancellation

Runtime may cancel a stable job id through the established session. A pre-cancelled job must not be submitted as normal work.

## Boundaries

The protocol does not define:

- pack selection;
- canonical IR meaning;
- project file writes;
- transport/server registration;
- a template engine API;
- target-language import/export syntax.
