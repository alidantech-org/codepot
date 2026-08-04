# dryv-author

Code: `packages/python/dryv-author`

Status: active implementation under Dryv replanning. No implementation task is currently active.

`dryv-author` provides a clean authoring API and compiles authored definitions into the canonical Runtime IR owned by `dryv`.

It may validate authored declarations, create explicit relationships, and reduce repetition without hiding behavior. It must not generate application source code, select template packs, choose output paths, write generated files, serialize transport formats, or create a competing semantic model.

The governing architecture is documented in [`../dryv/`](../dryv/README.md).
