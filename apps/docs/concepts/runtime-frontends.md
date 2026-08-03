---
title: Runtime frontends
description: Why CLIs, web tools, editors, MCP servers, and AI integrations should share one runtime instead of duplicating engine behavior.
order: 34
---

# Runtime frontends

A frontend is any interface that lets a user or tool interact with Codepot.

Examples include:

- terminal commands;
- an editor extension;
- a web application;
- an MCP server;
- a desktop tool;
- an internal developer portal;
- a programmatic Node.js integration.

## The boundary

```text
frontend input and presentation
        ↓
typed runtime request
        ↓
shared compiler, templating, generation, and platform services
        ↓
typed runtime response and events
        ↓
frontend presentation
```

A frontend may decide how to collect input, show progress, visualize a plan, or ask for confirmation.

It should not independently decide:

- how contracts compile;
- how template variables resolve;
- which paths are safe;
- how manifests classify ownership;
- when cleanup is allowed;
- how diagnostics are structured.

## `codepotx-cli` as proof

`codepotx-cli` contains parser, runtime loader, event subscription, presenter, and exit-code behavior. It delegates domain work to `codepotx/runtime`.

That separation is the model for future JavaScript web, editor, and MCP clients.

## Final platform frontends

The Rust platform follows the same principle:

- the `codepot` CLI uses compiler and analysis crates;
- the LSP uses the persistent analysis host and editor-neutral providers;
- the VS Code extension remains a thin client;
- future web and MCP integrations should reuse stable runtime and semantic artifacts.
