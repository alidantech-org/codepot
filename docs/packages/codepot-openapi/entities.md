---
title: Entities, fields, relations, and constraints
description: Describe persistence intent without coupling contracts to one ORM or database.
product: codepot-openapi
package: codepot-openapi
order: 7
---

# Entities, fields, relations, and constraints

Entity metadata describes persistence and domain behavior that ordinary OpenAPI schemas do not express.

It is emitted under `x-codegen` and remains target-neutral. A generator can translate the same entity contract into TypeORM, Prisma, Django, SQL, or another project-owned template pack.

## Define entities

The package exports:

```ts
import {
  defineBaseEntities,
  defineEntities,
  defineEntityRelations,
} from 'codepot-openapi';
```

Base entities hold reusable persistence fields. Concrete entities connect those fields to resource models and storage behavior.

Typical metadata includes:

- entity name and owner;
- abstract or concrete status;
- backing schema;
- store and visibility intent;
- inherited base entities;
- declared and inherited fields;
- relations and constraints.

## Field behavior

Entity fields can express:

- persistence role;
- generated strategy;
- uniqueness and indexing;
- immutable, readonly, editable, managed, and selectable behavior;
- backend-only storage fields;
- query capabilities;
- validation and implementation notes.

These flags have distinct meanings:

| Flag | Meaning |
|---|---|
| `immutable` | Assignable at creation but not changed later |
| `readonly` | Visible to consumers but not accepted as editable input |
| `managed` | Owned by backend or infrastructure behavior |
| `selectable` | Available in ordinary projections and responses |
| `backend_only` | Stored or used internally but not part of public shapes |

Do not collapse them into one generic `readOnly` flag in templates.

## Relations

A relation records:

- cardinality;
- target entity;
- local and foreign fields;
- delete and update behavior;
- nullable and owning sides;
- inverse relation metadata.

Supported cardinality describes to-one and to-many relationships without naming a specific ORM decorator.

```text
Customer 1 ─── * Order
Order    * ─── 1 Customer
```

Generators should resolve both sides before emitting imports or relation declarations.

## Constraints

Entity constraints can represent:

- primary or unique fields;
- compound uniqueness;
- indexes;
- checks and rule expressions;
- target-specific implementation notes.

Constraint rules preserve their operation, fields, values, arguments, conditions, and result branches so a generator can choose the correct target-language form.

## Base entities

Use base entities for stable shared persistence meaning such as:

- IDs;
- created and updated timestamps;
- tenant ownership;
- soft-delete fields;
- audit ownership.

Do not use inheritance merely to reduce repeated TypeScript. Inheritance should represent real domain or storage behavior that every target needs to understand.

## Schema and entity separation

A schema describes API data shape. An entity describes persistence intent. They may reference one another, but they are not interchangeable.

For example:

- `User` may be a public response schema;
- `CreateUser` may be an input projection;
- `UserEntity` may include password hashes, indexes, and managed timestamps.

Keeping these concerns separate prevents a database model from becoming the accidental public API.

## Best practices

- Keep entity names stable once templates depend on them.
- Mark behavior explicitly instead of making every generator infer it.
- Define relation ownership and delete behavior deliberately.
- Preserve backend-only fields outside public schema projections.
- Add constraints to the contract only when they are part of intended application semantics.
- Let project templates choose framework syntax; keep the contract target-neutral.