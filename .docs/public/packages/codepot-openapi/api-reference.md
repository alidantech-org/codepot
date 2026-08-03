---
title: Public API reference
description: Understand the supported package exports and choose the correct entry point for contract authoring, compilation, validation, and generation.
product: codepot-openapi
package: codepot-openapi
order: 11
---

# Public API reference

The package currently publishes one supported root entrypoint:

```ts
import { ... } from 'codepot-openapi';
```

Do not import internal source paths.

## Core builders

```ts
defineVersionContract
defineResource
defineFrontend
defineAccess
defineHooks
defineBaseEntities
defineEntities
defineEntityRelations
```

Use these APIs to author the contract graph.

## Package configuration

```ts
definePackageConfig
resolvePackageConfig
resolveCompileOptions
PackageOutputFormat
```

Most applications need only `definePackageConfig`.

## Schema and components

```ts
schema
defineSchemas
defineParameters
defineRequestBodies
defineResponses
ComponentBucket
ParameterLocation
```

The package also exports the corresponding registry, definition, and reference types.

## Routes

```ts
HttpMethod
```

Route builders are normally accessed through a resource's `defineRoutes()` result. Public route types are available for extensions and typed integrations.

## Compiler and validation

```ts
compileOpenApi
validateContract
validateOpenApiDocument
```

Relevant result types include:

```ts
CompileResult
CompileSuccessResult
CompileFailureResult
ValidationResult
ValidationIssue
OpenApiValidationResult
```

## Generation and output

```ts
generateOpenApi
writeOpenApiFiles
resolveOutputConfig
createOpenApiFileName
createDebugFileName
```

Use `generateOpenApi` for the full programmatic workflow.

## High-level facade

```ts
OpenApiTs
```

The facade exposes package-level initialization and generation operations through the `OpenApiTsApi` contract.

## OpenAPI constants and types

```ts
OpenApiVersion
OpenApiContentType
OpenApiRefPattern
```

Document types include `OpenApiDocument`, `OpenApiInfo`, `OpenApiComponents`, `OpenApiPaths`, `OpenApiOperation`, and `OpenApiServer`.

## `x-codegen`

```ts
CODEGEN_EXTENSION_KEY
XCodegenKind
XCodegenDtoRole
XCodegenEntityVariant
XCodegenAccess
applyCodegenMetadata
resolveCodegenKind
isModelSchema
isDtoSchema
isEnumSchema
isPrimitiveSchema
isObjectSchema
```

## Naming helpers

```ts
toSchemaName
componentRefToSchemaName
modelRefToSchemaName
```

## Logging

```ts
CompilerLogger
```

## Export stability

The root exports are the supported compatibility boundary. Internal file organization, compiler passes, registry implementations, and private builder helpers may change without preserving direct imports.

When a type is exported, use it to extend or inspect the package. Avoid reconstructing equivalent structural types because new fields can be added as the compiler evolves.