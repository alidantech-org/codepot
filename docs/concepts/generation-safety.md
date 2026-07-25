---
title: Generation safety
description: The project-wide guarantees for planning, file ownership, cleanup, immutable files, commands, cancellation, and rollback.
order: 35
---

# Generation safety

Generated code must be predictable enough to run repeatedly without treating the user's repository as disposable output.

## Plan before mutation

The generator should resolve and validate the complete output plan before changing files.

Failures such as unknown variables, duplicate output paths, invalid selectors, unsafe paths, and unresolved dependencies should stop before mutation.

## Render before mutation

All virtual files should render successfully before writes begin. A template error halfway through rendering must not leave a partially generated project.

## Explicit ownership

Generated and custom ownership must not mix implicitly.

Common classifications include:

- **managed** — Codepot may update the file and record its digest;
- **immutable** — Codepot may create the file once but not overwrite it;
- **protected** — generation is not allowed to write there;
- **user-edited** — a stale file no longer matches the generated digest and must be preserved;
- **unmanaged** — the manifest does not claim ownership.

## Guarded cleanup

A clean root is an allowed scope, not a command to recursively delete everything inside it.

A stale file should be removed only when it was previously managed, is no longer planned, remains inside an allowed scope, and still matches its previous generated digest.

## Commands

Before and after commands belong to the consumer project. Required failures should stop or roll back the task. Optional failures should become diagnostics.

Dry runs should not execute real project commands.

## Transactions and cancellation

Transactional generation should snapshot affected bytes and restore them after write failures, cancellation after mutation, or required after-command failures.

Cancellation before mutation should exit without filesystem changes.

## Frontend consistency

A CLI, editor, web UI, or MCP tool may present safety decisions differently, but none should bypass the shared runtime policy.
