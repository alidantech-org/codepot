---
title: codepot-openapi
description: Complete documentation for the supported TypeScript-first OpenAPI contract engine.
product: codepot-openapi
package: codepot-openapi
order: 1
---

# `codepot-openapi`

`codepot-openapi` is the supported TypeScript-first contract engine in the current Codepot prototype workflow.

It lets a project describe API contracts, reusable schemas, resources, routes, persistence metadata, access rules, runtime hooks, frontend intent, and implementation guidance in typed TypeScript. The compiler emits portable OpenAPI 3.1 JSON or YAML and resolves Codepot-specific meaning into `x-codegen` metadata.

## Package status

- npm package: `codepot-openapi`
- current package version: `0.0.4`
- runtime: Node.js 20 or newer
- module formats: ESM, CommonJS, and TypeScript declarations
- peer dependency: Zod 4
- binary: `codepot-openapi`

The package is active and supported. It is the mature contract-authoring side of the prototype workflow, while `codepotx` is the official JavaScript runtime rewrite.

## What the package owns

- versioned OpenAPI contracts;
- shared property registries and Zod-backed schemas;
- schema projections and reference wrappers;
- reusable parameters, request bodies, and responses;
- resources and route operations;
- entity, relation, and constraint metadata;
- access policies and runtime hooks;
- frontend screens and components;
- `x-codegen` metadata resolution;
- contract validation, OpenAPI compilation, file writing, and CLI commands.

## Learning path

1. [Install and create a contract](/docs/packages/codepot-openapi/getting-started)
2. [Understand the compiler architecture](/docs/packages/codepot-openapi/architecture)
3. [Configure package output](/docs/packages/codepot-openapi/configuration)
4. [Define properties, schemas, and refs](/docs/packages/codepot-openapi/schemas)
5. [Define resources and routes](/docs/packages/codepot-openapi/resources-routes)
6. [Add entities and relations](/docs/packages/codepot-openapi/entities)
7. [Add access, hooks, and frontends](/docs/packages/codepot-openapi/application-metadata)
8. [Understand `x-codegen`](/docs/packages/codepot-openapi/x-codegen)
9. [Generate and validate output](/docs/packages/codepot-openapi/generation-validation)
10. [Use the public API safely](/docs/packages/codepot-openapi/api-reference)

## Typical workflow

```text
TypeScript contract source
        ↓ compileOpenApi
validated OpenAPI 3.1 document
        ↓ generateOpenApi / CLI
JSON and YAML files
        ↓ optional codepotg task
normalized generator context
        ↓ Jinja template pack
project-owned generated code
```

## Install

```bash
npm install codepot-openapi zod
```

Continue with [Getting started](/docs/packages/codepot-openapi/getting-started).