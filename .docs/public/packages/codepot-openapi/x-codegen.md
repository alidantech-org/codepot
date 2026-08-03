---
title: x-codegen metadata
description: Understand how Codepot-specific software intent is resolved into portable OpenAPI extensions.
product: codepot-openapi
package: codepot-openapi
order: 9
---

# `x-codegen` metadata

`x-codegen` is the extension boundary that carries Codepot-specific semantics through an otherwise standard OpenAPI document.

The extension does not replace OpenAPI. Ordinary OpenAPI tools can ignore it, while Codepot-aware generators can use it to preserve application meaning.

## Extension key

The public constant is:

```ts
import { CODEGEN_EXTENSION_KEY } from 'codepot-openapi';
```

The compiler applies metadata only to supported targets and resolves references before output.

## Metadata categories

The package exposes typed metadata for:

- primitives and models;
- DTO roles and projections;
- enums;
- resources;
- entities and entity variants;
- queries and operation roles;
- access policies;
- UI and frontend intent;
- runtime transport and hooks;
- cache effects;
- implementation information.

## Codegen kind

`XCodegenKind` and `resolveCodegenKind` classify a schema or contract object into a stable generator category.

Helpers such as `isModelSchema`, `isDtoSchema`, `isEnumSchema`, `isPrimitiveSchema`, and `isObjectSchema` let tools inspect resolved kinds without reproducing compiler logic.

## DTO roles

`XCodegenDtoRole` distinguishes shapes such as:

- create input;
- update input;
- query input;
- path or parameter input;
- request body;
- response DTO;
- general projection.

Roles help a generator place files, choose validation behavior, and avoid naming every object as a database model.

## Entity variants

`XCodegenEntityVariant` communicates whether a schema represents a base, concrete, projected, or persistence-oriented entity shape.

Entity metadata can carry field behavior, relations, constraints, visibility, storage intent, and backend-only fields.

## UI metadata

`CodegenUiMeta` and resolved UI metadata preserve:

- authored enabled state;
- inference preference;
- effective inherited state;
- role;
- inference source and reason.

A generator can show why an item was included instead of silently guessing.

## Operation effects

Operation effects can describe:

- cache reads and invalidation;
- cookie changes;
- headers;
- runtime hooks;
- transport requirements.

These are semantic facts. The target template decides how to express them.

## Reference pointers

`XCodegenRefPointer` keeps metadata references stable and serializable. The compiler resolves pointers only after registries are complete and reports unresolved targets.

## Applying metadata programmatically

```ts
import { applyCodegenMetadata } from 'codepot-openapi';
```

Most contract authors should use typed builders. `applyCodegenMetadata` is useful for compiler integrations or controlled extension points that already own a valid target.

## Compatibility rules

- Keep unknown `x-*` values intact when downstream tooling supports them.
- Do not infer a Codepot kind solely from a schema name when resolved metadata exists.
- Prefer named normalized metadata over raw extension inspection.
- Treat operation IDs, resource IDs, entity IDs, and frontend IDs as stable references.
- Remove inheritance metadata from enum and non-object shapes through the compiler helpers rather than ad hoc template logic.

## Plain OpenAPI compatibility

A document without `x-codegen` still works with `codepotg` through OpenAPI inference. Rich metadata reduces guessing and preserves authored intent when multiple implementations would otherwise be plausible.