# Diagnostics, events, results, and cancellation

## Diagnostic model

Diagnostics are immutable typed values with:

- stable code;
- severity: info, warning, error, fatal;
- human message;
- source span when available;
- owning subsystem;
- related spans;
- structured details;
- suggested action;
- documentation reference.

Diagnostic codes are namespaced by subsystem, for example:

```text
CFG0001
PACK0104
LANG-TS0201
ENGINE-JINJA0302
PLAN0405
WRITE0502
CMD0601
```

Expected validation failures are returned as diagnostics. Tests assert codes and structured fields, not full prose when wording is not part of the public contract.

## Source spans

Configuration parsers preserve:

- file or virtual source name;
- start and end line;
- start and end column;
- document path;
- original key spelling.

This enables errors such as:

```text
codepotg.yaml:42:9 CFG0012
Unknown pack option 'generateRepostories'.
Did you mean 'generateRepositories'?
```

Pack, template, source specification, and generated-output diagnostics should retain provenance chains.

## Events

Events describe work in progress and completed state changes. Events are immutable and contain operation/session ID, timestamp, event type, phase, optional progress, and structured payload.

Event sinks are ports. A failing observer must not corrupt generation unless the host explicitly configures fail-fast event delivery.

## Results

All application results include:

- status enum;
- tuple of diagnostics;
- operation-specific payload;
- readiness actions;
- timing summary;
- reproducibility metadata such as plugin and pack versions.

Collections are immutable tuples or read-only mappings.

## Cancellation

Cancellation is cooperative and checked at stable boundaries:

- after configuration parsing;
- after pack resolution;
- between source records;
- between template invocations;
- before command execution;
- before transactional commit.

Cancellation before commit leaves destination state unchanged. Cancellation after commit starts returns a typed outcome that accurately records whether the transaction completed or rolled back.

## Error boundaries

- configuration and semantic errors become diagnostics;
- plugin contract violations become plugin diagnostics;
- command failures become command results and diagnostics;
- writer failures trigger rollback and writer diagnostics;
- programmer errors remain exceptions but are wrapped at public boundaries with session context.

No core layer calls `sys.exit` or prints errors directly.
