---
title: codepot CLI
description: The final Codepot command-line interface, running under the codepot command in the Rust platform.
product: codepot-cli
order: 22
---

# `codepot` CLI

The final Codepot command-line interface runs under:

```bash
codepot
```

This is distinct from the JavaScript rewrite's temporary release-line command:

```bash
codepotx
```

and from the prototype package commands:

```bash
codepot-openapi
codepotg
```

## Current commands

The Rust repository currently documents:

```bash
codepot check
codepot check --format json
codepot format
codepot format --check
codepot compile
codepot inspect modules
codepot inspect imports src/app/main.codepot
codepot inspect symbols
codepot inspect ast src/app/main.codepot
codepot inspect ir src/app/main.codepot
codepot doctor
codepot lsp --stdio
```

## Responsibilities

The CLI is a frontend over shared compiler and analysis crates. It should not define a second parser, semantic analyzer, formatter, or diagnostic model.

- `check` runs semantic analysis without writing compiler output.
- `format` uses the canonical Rust formatter.
- `compile` emits the configured deterministic IR output.
- `inspect` exposes modules, imports, symbols, AST, and IR for debugging and tooling.
- `doctor` checks project configuration, roots, module uniqueness, server availability, and semantic analysis.
- `lsp --stdio` provides a CLI fallback for launching the language server.

## Build from source

```bash
cargo build -p codepot-cli --bin codepot
```

The generated binary is typically:

```text
target/debug/codepot
target/debug/codepot.exe
```

## Automation

```bash
codepot check --format json
codepot format --check
```

JSON diagnostics are suitable for editor, CI, and other machine-readable integrations.

## Release links

Public release-download and package-registry links are reserved as TBD until an official distribution channel is published.
