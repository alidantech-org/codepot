# dryv

Code: `packages/python/dryv`

Status: active implementation; architecture cleanup, rewrite, improvement, and replanning are in progress. No implementation task is currently active.

## Current architecture

```text
Authoring
    -> Canonical Dryv Runtime IR
    -> Templating
    -> Usage and generated output
```

Responsibilities remain separate:

- authoring defines software and compiles into Runtime IR;
- Runtime IR is the only semantic authority;
- the runtime owns IR validation, serialization, loading, inspection, planning, and safe generation;
- template packs own selection, binding, rendering, output paths, and generated dependencies;
- usage connects authored input or serialized IR with packs, options, bindings, and destinations;
- the CLI presents the runtime without becoming a second semantic system.

Generation must remain deterministic, explainable, portable, and safe around managed and unmanaged files.

## Replanning direction

The next plan will simplify and harden the implemented architecture without restoring deprecated task ledgers or copying old design documents. New tasks will be created only after a concrete plan is approved.

Related packages:

- [`../dryv-author/`](../dryv-author/README.md)
- [`../dryv-cli/`](../dryv-cli/README.md)
- [`../dryv-template-jinja/`](../dryv-template-jinja/README.md)
- [`../dryv-language-typescript/`](../dryv-language-typescript/README.md)
- [`../dryv-language-dart/`](../dryv-language-dart/README.md)
