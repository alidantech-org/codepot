---
title: Architecture and compilation
description: Understand the builders, registries, validation passes, compiler, and output pipeline.
product: codepot-openapi
package: codepot-openapi
order: 3
---

# Architecture and compilation

`codepot-openapi` separates authored TypeScript builders from the plain OpenAPI document that leaves the compiler.

## Authoring layer

The authoring layer contains mutable builders and registries used while a contract file executes:

```text
defineVersionContract
  ├─ shared properties
  ├─ reusable components
  ├─ resources
  │   ├─ schemas
  │   ├─ routes
  │   ├─ entities
  │   ├─ access
  │   ├─ hooks
  │   └─ frontend metadata
  └─ version defaults and information
```

References returned by builders are stable authoring handles. They allow later declarations to point to previously registered properties, schemas, operations, entities, and metadata without copying definitions.

## Compilation layer

`compileOpenApi` reads one version builder and produces a deterministic plain object:

```text
builder registries
    ↓ normalize and resolve references
contract validation
    ↓ apply OpenAPI components and paths
x-codegen metadata resolution
    ↓ final document validation
OpenAPI 3.1 document
```

The emitted document contains no builder instances, Zod instances, functions, or mutable registry objects.

## Validation stages

Validation is intentionally split:

1. **Authoring validation** checks duplicate names, invalid references, route conflicts, metadata ownership, and unsupported combinations.
2. **Compiler resolution** converts refs and projections into schemas and OpenAPI component references.
3. **OpenAPI validation** checks the generated document through the package validator and configured validation policy.

`validateContract` exposes contract-level issues. `validateOpenApiDocument` exposes document-level results.

## Reference resolution

The compiler resolves:

- property references;
- schema references and projections;
- parameter, request-body, and response components;
- route parameter sources;
- entity and relation targets;
- access and runtime-hook references;
- cache invalidation operation targets;
- frontend operation and schema uses.

Resolution is completed only after the relevant registry exists. This allows forward references where the public builder contract supports them while still reporting unresolved names deterministically.

## Output layer

`generateOpenApi` combines compilation and writing. `writeOpenApiFiles` owns JSON/YAML serialization and naming.

Output files use the configured folder, prefix, formats, and optional debug prefix. The same compiler result can also be consumed in memory by another Node.js application.

## Public boundaries

Use published exports from `codepot-openapi`. Do not import internal source folders such as `compiler/passes` or individual registry implementations. Internal layout can change without a public compatibility promise.

## Relationship to codepotg

`codepot-openapi` produces the portable contract boundary. `codepotg` consumes that boundary and builds a generator-specific normalized model. The two packages do not share mutable runtime objects.