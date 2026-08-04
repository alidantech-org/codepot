# <TASK-ID>: <Title>

```yaml
id: <TASK-ID>
title: <Title>
status: draft
priority: normal
owner: unassigned
component: <path>
subsystem: <name>
depends_on: []
conflicts_with: []
allowed_paths: []
forbidden_paths: []
required_reading: []
```

## Problem

Describe the observed problem and affected users or workflows.

## Evidence

List exact files, failing behavior, measurements, logs, or prior decisions.

## Scope

State what this task will change.

## Non-goals

State nearby work this task must not perform.

## Architecture constraints

List the governing boundaries that cannot be weakened.

## Expected behavior

Describe observable behavior after completion.

## Acceptance criteria

- [ ] Each criterion is concrete and independently checkable.

## Validation

```text
<exact commands and manual checks>
```

## Documentation and release impact

List canonical docs, public APIs, migration notes, package metadata, or release notes that must change.

## Completion evidence

```text
Commit: <sha or range>
Tests: <exact commands and results>
Docs: <paths>
Acceptance: <confirmed criteria>
Remaining: <limitations or none>
Follow-up: <task or none>
```
