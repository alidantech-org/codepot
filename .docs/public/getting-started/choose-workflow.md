---
title: Choose a workflow
description: Select the right Codepot packages based on maturity, input format, templates, and integration needs.
order: 4
---

# Choose a workflow

Use the workflow that matches the maturity and integration needs of your project.

## Decision table

| Need | Recommended workflow | Why |
|---|---|---|
| Production-used OpenAPI generation now | `codepot-openapi` + `codepotg` | The most mature, supported workflow with Jinja packs and real-project usage |
| Author a typed OpenAPI contract | `codepot-openapi` | Direct TypeScript builders, Zod refs, OpenAPI JSON/YAML, and `x-codegen` metadata |
| Generate from an existing OpenAPI document | `codepotg` | OpenAPI 3.0/3.1 loading, inference, bundled languages, and custom Jinja packs |
| Evaluate or contribute to the official JavaScript rewrite | `codepotx` | Frontend-neutral runtime, stable artifacts, Handlebars packs, safe planning and writes |
| Use the official JavaScript runtime from a terminal | `codepotx-cli` | Thin CLI frontend that delegates to the project-local runtime |
| Build a web, editor, MCP, or embedded JavaScript frontend | `codepotx/runtime` | Reuse runtime operations without moving engine behavior into the UI |
| Explore the final strongly typed language | Codepot Lang | Rust compiler, semantic analysis, IR, CLI, LSP, formatter, and editor tooling |
| Add current VS Code language support | Codepot language extension | Thin VS Code client backed by the Rust LSP |

## Choose the prototype workflow when

- you already use OpenAPI as a source or interchange format;
- you need Python and Jinja template packs;
- you need bundled TypeScript, Next.js, Dart, or debug templates;
- you depend on the current normalized inference model;
- production maturity matters more than the final runtime architecture.

Start with [Prototype workflow](/docs/prototype-workflow).

## Choose `codepotx` when

- you are developing the official stable rewrite;
- you want a TypeScript runtime that is independent of one frontend;
- you need strict artifact boundaries and dependency-direction rules;
- you want Handlebars template compilation, variable catalogs, generation plans, transactions, and runtime operations in one JavaScript package;
- you are ready to evaluate pre-release workspace packages rather than a completed public release.

Start with [codepotx workflow](/docs/codepotx-workflow).

## Choose Codepot Lang when

- you are contributing to the final language design;
- you need compiler or LSP work rather than a production generator migration;
- you want software intent expressed in a purpose-built strongly typed language;
- you understand that interpreter and code-generation capabilities remain extension points under development.

Start with [Codepot Platform](/docs/codepot-platform).

## Do not infer replacement from age

`codepot-openapi` and `codepotg` are older than `codepotx`, but they are not abandoned. They remain supported because they are mature and useful.

`codepotx` is the official long-term JavaScript rewrite, but its role does not make the prototypes invalid before migration readiness is proven.
