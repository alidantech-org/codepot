---
title: Codepot platform
description: "The final Rust-based Codepot platform: language, compiler, runtime, CLI, LSP, extension, web, MCP, and generators."
product: codepot-runtime
order: 20
---

# Codepot platform

The final Codepot platform is the Rust-based direction that places a strongly typed semantic language at the center of the project.

It is broader than a code generator. The goal is one coherent system for expressing software meaning, compiling it, analyzing whole workspaces, supporting editors, producing target-neutral IR, and exposing the same capabilities through terminal, web, MCP, and future generator frontends.

## Platform shape

```text
Codepot Lang
    ↓
source + package system + standard library
    ↓
lexer + parser + semantic analysis
    ↓
target-neutral IR + persistent analysis host
    ↓
codepot CLI
Codepot LSP
language extension
future generators and runtime
web tooling
MCP and AI integrations
```

## Current implemented areas

The `codepot_lang` repository currently contains:

- kernel types, identifiers, spans, and traits;
- source readers and shared source storage;
- `Codepot.toml` configuration;
- lossless lexer and recoverable parser;
- filesystem package and import resolution;
- source or embedded standard-library selection;
- symbols, generics, references, inheritance, and strong semantic analysis;
- target-neutral IR and deterministic YAML serialization;
- persistent VFS-backed workspace analysis;
- editor-neutral IDE providers;
- LSP adapter;
- canonical formatter;
- one-shot compiler;
- the `codepot` CLI;
- a thin VS Code extension client;
- trait-first code-generation and interpreter extension points.

## Current boundaries

Codepot Lang 0.3 compiles source into an in-memory semantic program and deterministic YAML IR.

The interpreter and final code-generation runtime remain extension points. Planned web and MCP products are not released and should remain clearly marked as planned in documentation and UI.

## Ownership layers

1. **Kernel** — Rust-owned syntax mechanics, identifiers, spans, expressions, and primitive types.
2. **Standard library** — Codepot-authored world values and software constructs marked with `library;`.
3. **Project foundation** — project-owned bases, envelopes, contexts, and policies.
4. **Feature modules** — application entities, inputs, outputs, APIs, screens, workflows, and rules.

## Why this follows `codepotx`

`codepotx` establishes frontend-neutral runtime operations and stable artifact boundaries in JavaScript.

The Rust platform goes further by giving software intent a purpose-built language, compiler, package system, semantic model, and editor tooling. Validated project concepts move forward, but implementation details are redesigned for the language and compiler architecture.

## Related pages

- [Codepot Lang](/docs/codepot-lang)
- [codepot CLI](/docs/codepot-cli)
- [Codepot LSP](/docs/codepot-lsp)
- [Language extension](/docs/codepot-extension)
- [Web and MCP](/docs/codepot-web-mcp)
