# dryv-template-jinja

Code: `packages/python/dryv-template-jinja`

Status: active implementation under Dryv replanning. No implementation task is currently active.

This package adapts Jinja to Dryv's template-engine contract. It renders values already selected and bound by the runtime and pack; it does not redefine software meaning, invent hidden context, choose project structure, or own output transactions.

The governing architecture is documented in [`../dryv/`](../dryv/README.md).
