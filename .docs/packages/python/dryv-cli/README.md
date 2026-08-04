# dryv-cli

Code: `packages/python/dryv-cli`

Status: active implementation under Dryv replanning. No implementation task is currently active.

`dryv-cli` is the terminal frontend for the Dryv runtime. It exposes planning, generation, inspection, serialization, and plugin information through stable human and machine output.

The CLI does not own Runtime IR meaning, template selection semantics, generation state, or file-safety rules. Those remain runtime responsibilities. CLI failures must produce reliable diagnostics and process exit codes.

The governing architecture is documented in [`../dryv/`](../dryv/README.md).
