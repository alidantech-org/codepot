# Task 00 — Build VS Code as a Dryv Project Client

Status: [ ]
Owner: planned `apps/vscode`
Depends on: TypeScript `dryv-client` Tasks 00–01 and stable `dryv-api`
Validation: extension integration tests, workspace safety tests

## Goal

Build the VS Code frontend as a Project Client on top of the shared TypeScript Dryv client. VS Code owns workspace discovery/presentation/local apply; Dryv Runtime remains behind `dryv-api`.

## Core flow

```text
VS Code workspace
→ discover dryv.yaml
→ collect/hash logical resources
→ connect to local or remote dryv-api
→ start build/upload missing resources
→ stream progress/diagnostics/artifacts
→ preview planned changes/diffs
→ safely apply accepted WriteInstructions locally
→ report apply acknowledgements
```

## Workspace responsibilities

Use Node project utilities from the TypeScript Dryv client for:

- workspace/project-root discovery;
- local/private pack/resource collection;
- previous managed-output manifest loading;
- content hashing;
- atomic safe apply;
- managed-output manifest persistence after successful apply.

Do not duplicate these mechanics inside extension commands where reusable client code already owns them.

## UX responsibilities

VS Code may provide:

- build/plan commands;
- live progress and structured diagnostics;
- generated artifact tree;
- per-file preview/diff;
- trace/explanation views;
- apply/refuse/cancel actions;
- local/remote API connection status;
- renderer/author capability diagnostics from the API when relevant.

UI must not recalculate semantic plan decisions.

## Local/remote behavior

A future local companion process may host `dryv-api`; remote URL mode must use the same client protocol. The extension must not import Python Runtime code or assume Runtime and editor share a process/filesystem.

## Safety

- apply only project-relative validated instructions;
- preserve expected-hash conflict checks;
- do not silently overwrite user edits;
- never transmit Git credentials;
- clearly distinguish generated render completion from successful local apply.

## Non-goals

- Do not embed Dryv Runtime.
- Do not implement template rendering.
- Do not create independent pack/IR semantics.

## Allowed paths

- planned `apps/vscode/**`
- `.docs/apps/vscode/**`
- shared TypeScript Dryv client integration only

## Acceptance criteria

- extension can operate against local or remote `dryv-api` using the same protocol.
- resource collection and writes use shared project-client utilities.
- progress/diagnostics/artifacts are visible and cancellable.
- user-modified files are protected by expected-hash rules.
- no engine internals are bundled into the extension.

## Validation

Test workspace discovery, remote/local API config, build stream, preview, safe apply, user-edit conflict, cancellation and protocol/version mismatch using extension integration fixtures. Run extension/Node checks and `git diff --check`.
