# Dryv Author Session Protocol v1

## Purpose

This document is the language-neutral contract between Dryv Runtime and an established Author Session. Python classes under `dryv.features.authoring` implement this contract but do not define the wire format by themselves.

An Author Backend is an independent program or service whose semantic output is Canonical Dryv Runtime IR. The protocol is transport-neutral; Dryv Engine does not host the backend connection or choose HTTP, WebSocket, local IPC, or another transport.

## Version

Protocol version: `1`

The requested Canonical Dryv IR version is negotiated independently from the Author Session protocol version.

## Backend hello

An Author Backend advertises:

```text
backend id
backend version
backend fingerprint
supported source kinds/languages
supported Canonical IR versions
supported Author Session protocol versions
streaming support
maximum concurrency/capacity
```

The fingerprint identifies output-affecting backend behavior for reproducibility and diagnostics.

## Author request

A request contains:

```text
protocol version
stable job/build id
requested Canonical IR version
source kind
logical source resource ids
optional source media types
backend-specific options declared by project configuration
```

Source acquisition remains outside Dryv Engine. Requests refer to logical resources already supplied through the Runtime boundary rather than arbitrary host filesystem paths.

## Author messages

An Author Session may stream these message kinds:

### Progress

```text
message
optional completed amount
optional total amount
```

### Diagnostic

```text
stable code
message
severity
```

### Canonical IR record

One Canonical Dryv IR representation record, suitable for the Serialization Feature record decoder. Large authoring results should prefer streamed canonical records.

### Canonical IR document

A complete versioned Canonical Dryv IR document with media type and bytes. Supported representations include the approved JSON/YAML transport forms.

### Complete

```text
job id
backend fingerprint
```

Completion terminates one successful author result stream.

## Representation rules

A backend may return exactly one representation mode per job:

- one complete Canonical IR JSON/YAML document; or
- a stream of Canonical IR records, normally JSONL-backed.

A backend must not mix document and record representations within one job. Backend-private semantic models are not accepted as Runtime authority.

After decoding, Dryv validates the resulting Canonical IR before any pack/planning work may consume it.

## Validation rules

Dryv rejects author work when:

- requested protocol version is unsupported;
- requested IR version is unsupported;
- requested source kind is unsupported;
- the backend mixes canonical representation modes;
- the stream completes without canonical IR;
- completion job id differs from the request;
- backend fingerprint changes during the job;
- decoded Canonical IR fails Runtime validation.

## Precompiled IR

When project usage supplies precompiled Canonical Dryv IR, Runtime bypasses Authoring entirely. No Author Session is required.

## Cancellation

Runtime may cancel a stable author job through the established session. A pre-cancelled job must not be submitted as normal work.

## Boundaries

The Author Session protocol does not define:

- an authoring DSL;
- pack selection;
- template context;
- rendering;
- output paths;
- project filesystem writes;
- source Git/filesystem acquisition;
- server/connection registration.
