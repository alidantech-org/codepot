---
title: Authoring contracts
description: Define reusable typed contracts that compile directly into Codepot's stable authoring artifact.
order: 4
---

# Authoring contracts

Authoring is the user-facing TypeScript layer. Its public builders preserve the previous Codepot contract style while compiling directly to a deterministic `CompiledAuthoringArtifact`.

## Public schema namespaces

```ts
import { schema, z } from 'codepotx';
```

Use `z` when migrating existing contracts that previously imported Zod. Use `schema` for preferred Codepot-owned authoring, including Codepot composition helpers.

```ts
const Email = schema.primitive(schema.string().email());
const Profile = schema.composite({
  email: Email,
});
```

Codepot deliberately curates the exposed Zod-compatible surface. Zod remains an internal runtime dependency, not a peer dependency.

## Supported authoring areas

- shared and resource properties;
- schemas and projections;
- parameters, request bodies, and responses;
- resources, operations, sources, and cache invalidation;
- access and hooks;
- entities, lifecycle metadata, constraints, and relations;
- frontend metadata;
- project information and defaults.

## Field defaults

Fields are selectable, editable, and mutable by default. Use only outlier declarations:

```ts
field.immutable();   // settable on create, blocked on update
field.managed();     // backend/system owned and readonly
field.select(false);
field.edit(false);
```

## Cache invalidation

The current narrow cache contract supports route invalidation only:

```ts
route.cache((cache) => cache.invalidate.on('updateUser'));
```

The compiler validates referenced operation IDs. Read-cache keys, scopes, and tags are intentionally outside the current contract.
