---
title: Codepot language extension
description: The thin VS Code client for Codepot Lang, the Rust LSP, and offline syntax support.
product: codepot-extension
order: 24
---

# Codepot language extension

The Codepot language extension is the VS Code client under `codepot_lang/vcode`.

Extension ID:

```text
alidantech.codepot
```

The extension is intentionally thin. Parsing, type checking, semantic behavior, project analysis, and formatting stay in Rust.

## Supported files

```text
.pot
.code
.codepot
.cpt
```

## Features

- offline TextMate syntax highlighting;
- line, block, and documentation comments;
- import, function, generic, field, and documentation-tag highlighting;
- Rust LSP diagnostics and strong type checking;
- completion and automatic import insertion;
- hover documentation;
- definition, references, rename, symbols, semantic tokens, and signatures;
- canonical formatting, folding, and quick fixes;
- project commands for check, compile, doctor, modules, symbols, and imports.

## Build and package

```bash
cargo build -p codepot-lsp --bin codepot-lsp
cargo build -p codepot-cli --bin codepot

cd vcode
pnpm install --frozen-lockfile
pnpm verify
pnpm package
```

Install a locally built package:

```bash
code --install-extension ./codepot-0.3.0.vsix --force
```

## Development settings on Windows

```json
{
  "codepot.server.path": "${workspaceFolder}/target/debug/codepot-lsp.exe",
  "codepot.cli.path": "${workspaceFolder}/target/debug/codepot.exe",
  "[codepot]": {
    "editor.defaultFormatter": "alidantech.codepot",
    "editor.formatOnSave": true
  }
}
```

## Marketplace status

GitHub source is available. VS Code Marketplace and Open VSX links are reserved as TBD until publication is complete.
