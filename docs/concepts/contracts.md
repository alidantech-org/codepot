---
title: Contracts and artifacts
description: How Codepot moves from authored facts to portable OpenAPI, normalized generation contexts, and stable runtime artifacts.
order: 31
---

# Contracts and artifacts

A Codepot contract describes software facts that can be validated and reused independently from one generated application.

## Prototype contract boundary

`codepot-openapi` emits a standard OpenAPI document.

```text
TypeScript builder objects
        ↓ compile
OpenAPI JSON/YAML
        +
optional x-codegen metadata
```

OpenAPI provides a portable interchange boundary between TypeScript authoring and the Python generator.

## CodepotG normalized boundary

CodepotG loads OpenAPI and creates normalized domains for schemas, resources, operations, entities, relations, access, frontends, and generation facts.

Jinja templates consume that normalized context rather than directly traversing raw parser objects.

## `codepotx` artifact boundary

`codepotx` uses explicit versioned JSON-safe artifacts between layers:

```text
CompiledAuthoringArtifact
CompiledTemplatePack
TemplateVariableCatalog
GenerationPlan
RenderedGeneration
GenerationManifest
GenerationResult
```

This allows a CLI, web UI, editor, MCP server, or test adapter to exchange stable data without receiving compiler builders, Zod instances, Handlebars objects, or platform implementations.

## Codepot Lang IR boundary

The Rust compiler produces target-neutral semantic IR.

The compiler owns:

- symbol and type resolution;
- generic applications;
- references and inheritance;
- rules and provenance;
- public/private safety;
- package and import meaning.

Future generators should consume resolved IR and target-specific render models rather than reimplementing semantic analysis in templates.

## Contract design rule

A contract should describe meaning without hardcoding one target framework's entire folder or class structure.

Template packs and consumer configuration decide how that meaning becomes files.
