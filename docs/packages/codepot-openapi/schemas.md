---
title: Properties, schemas, and references
description: Define reusable fields, Zod-backed schemas, projections, arrays, optional values, and component references.
product: codepot-openapi
package: codepot-openapi
order: 5
---

# Properties, schemas, and references

Schemas are authored from Zod values, shared property references, and other schema references.

## Shared properties

Use `defineProperties` when fields such as IDs, timestamps, money, or audit metadata appear across resources.

```ts
const common = v1.defineProperties('Common', {
  id: z.string().uuid(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
}).ref;
```

A property registry keeps identity and metadata stable. Referencing `common.id` reuses the property definition rather than copying an unrelated Zod value.

## Resource schemas

```ts
const schemas = users.defineSchemas({
  User: {
    id: common.id,
    name: z.string().min(1).max(120),
    email: z.string().email(),
    createdAt: common.createdAt,
  },
  UserSummary: {
    id: common.id,
    name: z.string(),
  },
}).ref;
```

The returned ref group exposes schema references that can be used in routes, entities, frontend metadata, and later schemas.

## Projections

Reference wrappers support projections without redefining the source schema:

```ts
const createUser = schemas.User.omit({
  id: true,
  createdAt: true,
});

const patchUser = createUser.partial();
const userList = schemas.User.array();
```

Supported projection concepts include:

- `pick`;
- `omit`;
- `partial`;
- arrays;
- optional use;
- nullable use;
- chained projection steps.

Projection metadata remains available to `x-codegen`, allowing a generator to distinguish a named model from a create, update, query, parameter, or response projection.

## Primitive and composite fields

Schema fields may be:

- primitive Zod schemas;
- references to shared properties;
- references to other schemas;
- arrays of references;
- composite structures;
- projected references.

The compiler converts supported Zod constraints into OpenAPI schema keywords.

## Reusable components

The package also exposes builders for:

- schemas;
- parameters;
- request bodies;
- responses.

```ts
const parameters = v1.defineParameters({
  RequestId: {
    in: 'header',
    required: true,
    schema: z.string().uuid(),
  },
}).ref;
```

Use reusable components when a value has shared API meaning, not merely to avoid a few repeated lines.

## Naming

Component and model references are converted to legal schema names through public naming helpers such as `toSchemaName`, `componentRefToSchemaName`, and `modelRefToSchemaName`.

Choose stable PascalCase component names. Renaming a public schema changes OpenAPI references and may affect generated consumers.

## Best practices

- Define one canonical model and derive request/response projections from it when their meaning truly matches.
- Create separate schemas when two shapes have different business meaning even if their fields currently match.
- Keep shared properties small and semantically stable.
- Prefer explicit nullability and optionality.
- Validate recursive and circular references through the compiler instead of manually expanding them.
- Treat schema names and operation IDs as public compatibility boundaries.