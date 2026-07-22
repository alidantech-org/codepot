---
title: Generation safety
description: Understand manifests, clean scopes, immutable files, transactions, rollback, and cancellation.
order: 13
---

# Generation safety

## Rendering before mutation

Codepot resolves and validates the entire plan, then renders every virtual file in memory. Filesystem mutation begins only after rendering succeeds.

## No broad task cleanup

Task clean entries define allowed scopes. They do not recursively delete folders. Stale cleanup uses the previous task manifest and removes a file only when:

1. it was previously recorded as `managed`;
2. it is absent from the new manifest;
3. it is inside an allowed clean scope;
4. its current digest still equals the previous generated digest.

A user-edited stale file is preserved and reported as refused.

## Immutable files

An immutable file is created when absent and skipped on later runs. Codepot never overwrites it automatically.

## Transactions

Transactional tasks snapshot affected bytes before mutation. Write failures, cancellation after mutation, and required after-command failures restore previous files, remove newly created files, and restore or remove the manifest.

## Cancellation

Runtime cancellation propagates through planning, rendering, commands, writes, stale cleanup, and reports. Cancellation before mutation exits cleanly; cancellation after mutation uses rollback.

## Events

Stage, file, command, diagnostic, and runtime events are observational. Event listeners cannot change required control flow, and listener failures are isolated.
