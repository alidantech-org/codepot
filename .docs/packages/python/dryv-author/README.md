# dryv-author

Code: `packages/python/dryv-author`

Status: active implementation awaiting the approved backend refactor beginning at [`tasks/00-independent-canonical-ir-backend.md`](tasks/00-independent-canonical-ir-backend.md).

`dryv-author` is the Python Author Backend/toolkit. Its purpose is to provide a clean typed authoring API and compile authored definitions into the versioned Canonical Dryv IR contract.

The authored model must cover the same canonical meaning as every other Author Backend, including Contract/Group/Property, Schema and approved single-base extension, Policy, Failure, Event, Operation, StorageMapping, ValueSource, View, Workflow, Presentation, typed refs, tags, guidance and provenance.

The package may emit Canonical IR as JSON, YAML or JSONL and may later participate through the shared Author Backend HTTP/WebSocket protocol. It does not select packs, render templates, choose generated project paths, or write generated application files.

The target architecture removes dependency on Dryv Runtime implementation. `dryv-author` may consume language-neutral/generated protocol contracts needed to emit valid Canonical IR, but Dryv Engine remains the authoritative runtime validator/indexer/planner.

The governing architecture is documented in [`../dryv/`](../dryv/README.md).
