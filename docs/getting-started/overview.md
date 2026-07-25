---
title: Codepot overview
description: Understand the complete Codepot ecosystem, from production-used prototypes to the final Rust language platform.
order: 1
---

# Codepot

Codepot is a family of complementary tools for making software intent explicit, reusable, and safe to generate.

It helps teams describe contracts and software meaning once, apply approved template packs repeatedly, and expose the same project knowledge to developers, automation, editors, web tools, and AI agents.

Codepot is not one package replacing another overnight. It is a deliberate maturity pipeline:

```text
codepot-openapi + codepotg
        ↓ prove features in real projects
codepotx + codepotx-cli
        ↓ stabilize a frontend-neutral runtime
Codepot Lang + compiler/runtime + codepot CLI
+ LSP + extension + web + MCP
```

## The ecosystem today

### Mature working prototypes

[`codepot-openapi`](/docs/packages/codepot-openapi) and [`codepotg`](/docs/packages/codepotg) are supported, production-used packages.

- `codepot-openapi` authors typed TypeScript contracts and emits OpenAPI JSON or YAML with optional `x-codegen` metadata.
- `codepotg` consumes that OpenAPI, builds a normalized generation model, and renders Jinja template packs into project code.

These packages are where ideas can be tested against real applications before they are promoted into the official rewrite.

### Official JavaScript ecosystem

[`codepotx`](/docs/packages/codepotx) is the official stable rewrite and long-term JavaScript release line.

It is designed as a runtime rather than a terminal-only program. Typed authoring, template compilation, planning, rendering, safe writes, diagnostics, and runtime operations live in `codepotx`.

[`codepotx-cli`](/docs/packages/codepotx-cli) is one thin frontend for that runtime. The same runtime can later support a web interface, editor integration, MCP server, desktop tool, or embedded Node.js application.

### Final Codepot platform

[Codepot Lang](/docs/codepot-lang) is the ambitious Rust-based platform direction.

The final platform brings together:

- a strongly typed semantic language;
- compiler and persistent analysis runtime;
- the final `codepot` CLI;
- a Language Server Protocol implementation;
- the Codepot language extension;
- web tooling;
- MCP and AI integrations.

## What all generations share

Although the implementations differ, the project keeps the same core principles:

1. **Software intent should be explicit.** Contracts and semantic models should not be rediscovered from generated code on every task.
2. **Templates should remain reusable and user-owned.** Framework conventions, paths, naming, and implementation patterns belong to template packs.
3. **Generation should be inspectable.** Plans, variables, diagnostics, and file ownership should be visible before destructive work.
4. **Frontends should not own engine logic.** CLIs, editors, web tools, and AI integrations should call a reusable runtime.
5. **Features should mature through evidence.** Ideas are proven in working packages, stabilized in `codepotx`, and carried into the final language platform when their semantics are clear.

## Where to begin

- Browse [all package documentation](/docs/packages).
- Use [Choose a workflow](/docs/choose-workflow) to select the right package for your project.
- Follow [Getting started](/docs/getting-started) for the shortest practical path.
- Read [The ecosystem](/docs/ecosystem) for package relationships and status.
- Explore [Codepot Platform](/docs/codepot-platform) for the Rust language, CLI, LSP, extension, web, and MCP direction.
