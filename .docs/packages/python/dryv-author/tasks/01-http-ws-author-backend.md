# Task 01 — Add HTTP and outbound WebSocket Author Backend modes

Status: [ ]
Owner: `packages/python/dryv-author`
Depends on: Task 00 and `dryv-api` Author Backend connection task
Validation: protocol conformance tests, streaming/cancellation tests

## Goal

Allow the Python author backend to participate in remote/local Dryv builds through the shared Author Backend protocol without coupling the compiler to `dryv` Runtime.

## Modes

Support both:

1. **HTTP service mode** — expose a compile endpoint that accepts AuthorRequest resources/options and returns/streams Canonical Dryv IR plus diagnostics.
2. **Registered WebSocket client mode** — initiate an outbound persistent connection to `dryv-api`, register capabilities, receive author jobs, stream progress/IR records, and return completion/failure.

Direct file/CLI compilation to `dryv.ir.json|yaml|jsonl` remains supported and must not require either network mode.

## Capability registration

Advertise at minimum:

```text
backend id/version
supported source kind(s)
supported Canonical IR versions
streaming support
maximum concurrency/capacity
backend fingerprint
```

The backend fingerprint must change when compiler behavior that can affect emitted canonical output changes.

## Compile request behavior

The backend receives only logical source Resources/options declared for the job. It must not assume access to the Project Client's filesystem or Git credentials.

Compile output must use the same canonical wire contract as Task 00. Prefer JSONL record streaming for large results.

## Cancellation and failures

- support stable job IDs;
- cancel active compilation when requested;
- stop emitting records after terminal failure/cancellation;
- surface structured author diagnostics separately from transport failures;
- bound concurrent jobs and output buffering;
- support clean WS reconnect/re-registration without duplicating completed job results.

## Non-goals

- Do not embed Dryv Runtime.
- Do not load packs/templates.
- Do not generate project source files.
- Do not write user-project outputs.

## Allowed paths

- `packages/python/dryv-author/**`
- `.docs/packages/python/dryv-author/**`
- shared Author protocol generated/spec artifacts

## Acceptance criteria

- HTTP and WS modes produce canonical output identical to direct backend compilation for the same authored source/options.
- outbound WS registration works against a test `dryv-api` host.
- streaming/cancellation/capacity are bounded.
- the package remains independent from Dryv Engine internals.

## Validation

Add HTTP conformance tests, WS registration/job tests, large JSONL streaming, cancellation, reconnect, duplicate-job protection and direct-vs-network output equivalence. Run package typing/tests and `git diff --check`.
