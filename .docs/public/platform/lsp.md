---
title: Codepot LSP
description: The Rust language server backed by the same persistent analysis host and diagnostics as the Codepot compiler and CLI.
product: codepot-lsp
order: 23
---

# Codepot LSP

The Codepot language server is the editor-neutral Language Server Protocol adapter for Codepot Lang.

It uses the same package resolution, parser, semantic analysis, formatter, and diagnostics as the compiler and CLI.

## Architecture

```text
editor client
    ↓ LSP over stdio
codepot-lsp
    ↓
codepot-analysis persistent host
    ↓ overlay VFS for unsaved files
parser + packages + symbols + semantic analyzer
    ↓ immutable workspace snapshot
codepot-ide providers
```

## Current capabilities

- syntax and semantic highlighting;
- diagnostics for saved and unsaved files;
- module and imported-symbol completion;
- standard-library auto-import edits;
- field completion after member access;
- hover with project and std documentation;
- go to definition and references;
- safe project rename excluding std symbols;
- document and workspace symbols;
- typed function signature help;
- canonical formatting;
- folding and quick fixes.

## Build

```bash
cargo build -p codepot-lsp --bin codepot-lsp
```

The CLI can also host the server:

```bash
codepot lsp --stdio
```

## Discovery order used by the VS Code extension

1. `codepot.server.path`;
2. `CODEPOT_LSP_PATH`;
3. workspace `target/debug` or `target/release` native binary;
4. native `codepot-lsp` on `PATH`;
5. native `codepot` CLI using `lsp --stdio`;
6. a platform server bundled with the extension.

On Windows, discovery accepts native `.exe` files and avoids directly spawning pnpm command shims.

## Distribution status

Source and build instructions are available now. Public binary-release links remain TBD until official distribution is prepared.
