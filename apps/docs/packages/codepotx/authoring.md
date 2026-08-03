---
title: Typed authoring
description: Define contracts, schemas, resources, routes, fields, entities, access, hooks, and frontend intent in codepotx.
product: codepotx
package: codepotx
order: 4
---

# Typed authoring

The root `codepotx` entrypoint exposes the supported authoring DSL and compatibility exports.

```ts
import {
  defineCodepotConfig,
  defineVersionContract,
  defineResource,
  schema,
  z,
} from 'codepotx';
```

## Compiled boundary

Authoring builders are temporary. The authoring compiler converts them into `CompiledAuthoringArtifact`, a deterministic readonly JSON-safe object.

The artifact contains no Zod instances, mutable registries, functions, or frontend presentation state.

## Version contracts

```ts
const v1 = defineVersionContract({
  info: {
    title: 'Example API',
    version: '1.0.0',
  },
});
```

A version owns its components, resources, routes, entities, policies, hooks, frontends, and diagnostics.

## Schemas

```ts
const schemas = v1.defineSchemas({
  User: {
    id: z.string().uuid().managed(),
    name: z.string().min(1),
    email: z.string().email().immutable(),
  },
});
```

Field behavior is explicit:

- fields are selectable and editable by default;
- `.immutable()` allows creation input but blocks later updates;
- `.managed()` marks backend-owned readonly values;
- target templates receive stable behavior flags.

Schema refs support projections such as `pick`, `omit`, `partial`, arrays, optional, and nullable use where supported by the active DSL.

## Resources and routes

```ts
const users = v1.defineResource({
  name: 'users',
  route: '/users',
});

users
  .defineRoutes()
  .params(schemas.ref.User.pick({ id: true }))
  .routes((route) => ({
    listUsers: route.get('/').response(schemas.ref.User.array()),
    updateUser: route
      .patch('/:id')
      .body(schemas.ref.User.partial())
      .response(schemas.ref.User)
      .cache((cache) => cache.invalidate.on('listUsers')),
  }));
```

Route parameters are registered through the route definition model and reused by operations as designed. Operation IDs are stable references for caches, templates, clients, and runtime inspection.

## Cache metadata

The current contract intentionally limits cache invalidation to operation-ID references. This keeps invalidation deterministic and compiler-resolvable.

## Additional domains

The authoring layer includes typed domains for:

- shared properties and refs;
- components;
- entities, fields, relations, and constraints;
- access policies;
- runtime hooks and transport requirements;
- frontend screens and components;
- implementation information and documentation metadata.

## Source modes

Authoring sources can be resolved through supported local, package, Git, artifact, or memory descriptors, depending on the runtime and platform composition.

## Validation

The compiler validates:

- duplicate identities;
- cross-registry references;
- route parameters and operation IDs;
- projection and field behavior;
- cache invalidation targets;
- entity and relation references;
- access, hook, and frontend uses;
- artifact portability.

## Guidance

- Import only public entrypoints.
- Treat IDs and names as compatibility boundaries.
- Keep target-framework implementation in template packs.
- Compile before inspecting or serializing contract meaning.
- Use the artifact types from `codepotx/contract` for integrations.