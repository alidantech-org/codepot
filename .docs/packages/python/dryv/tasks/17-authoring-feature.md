# Task 17 — Build the Authoring Feature around Canonical IR sessions

Status: [ ]
Owner: `packages/python/dryv`
Depends on: Tasks 08, 10 and 12
Validation: author-session contract tests, IR-stream validation tests

## Goal

Create `features/authoring` as the runtime capability used only when `dryv.yaml` declares an Author Backend instead of supplying precompiled Canonical Dryv IR.

Author Backends are independent programs/services. Their only semantic responsibility is to produce Canonical Dryv IR in the approved versioned wire contract.

## Author-session contract

Define language-neutral/session-neutral contracts equivalent to:

```text
AuthorBackendHello / capabilities
AuthorRequest
AuthorProgress
AuthorIRRecord
AuthorComplete
AuthorDiagnostic
AuthorCancel
```

An Author Request may include:

```text
requested IR version
logical source resources
backend-specific options declared by project config
stable job/build id
```

Backend capabilities should include:

```text
backend id/version
supported source kinds/languages
supported IR versions
streaming support
capacity/concurrency where relevant
backend fingerprint
```

The exact wire schema belongs to shared protocol specifications, not Python-only classes.

## Canonical output

The backend may return:

- a Canonical IR JSON document;
- a Canonical IR YAML document;
- preferably a stream of Canonical IR JSONL records for large/incremental work.

Authoring Feature passes emitted records into Serialization + IR validation. It must not accept a backend-private semantic model as authoritative.

Precompiled `dryv.ir.*` inputs bypass Authoring Feature completely.

## Separation of responsibility

Authoring Feature does not:

- select packs;
- build template context;
- render templates;
- choose output paths;
- write generated files;
- understand the implementation language of the backend.

Author Backends do not need to import the Dryv Engine package.

## Session boundary

Runtime supplies an established Author Session. This Feature does not host HTTP/WS and does not manage inbound connection registration.

## Non-goals

- Do not rewrite `dryv-author` in this task; its independent backend migration is a separate package task.
- Do not implement filesystem/Git source acquisition inside Dryv Engine.
- Do not define authoring DSL syntax.

## Allowed paths

- `packages/python/dryv/src/dryv/features/authoring/**`
- shared protocol representations/specs owned by Dryv
- corresponding tests/docs

## Acceptance criteria

- Runtime can request IR from a deterministic fake Author Session.
- emitted records are validated as canonical IR before use.
- unsupported IR versions/backend capability mismatches fail clearly.
- precompiled IR path does not require an Author Session.
- no author implementation language dependency enters Dryv Engine.

## Validation

Test JSONL streaming, JSON/YAML document result, unsupported versions, malformed canonical records, cancellation, progress/diagnostic propagation and precompiled-IR bypass. Run architecture tests and `git diff --check`.
