# Entity Authoring

Entity metadata is a backend/storage semantic layer emitted under `x-codegen`. It is not ORM code, and it does not expose public API query parameters.

Use this order:

1. Define shared properties.
2. Define split base entity schemas.
3. Define split base entity metadata.
4. Define persistence-clean resource schemas.
5. Define resource entities from schemas.
6. Define entity relations.
7. Define public query, body, and response schemas explicitly.

## Shared Properties

```ts
export const sharedPropsRef = v1.defineProperties('Shared', {
  uuid: z.string().uuid(),
  dateTime: z.string().datetime(),
  username: z.string().min(1).max(100),
  roleName: z.string().min(1).max(120),
  token: z.string().min(1).max(500),
  boolean: z.boolean(),
}).ref;
```

## Split Base Schemas

Define each base schema in its own const so later schemas can safely extend earlier refs.

```ts
export const baseEntitySchemasRef = v1.defineSchemas({
  BaseEntity: {
    id: sharedPropsRef.uuid,
    createdAt: sharedPropsRef.dateTime,
    updatedAt: sharedPropsRef.dateTime,
  },
}).ref;

export const softDeletableEntitySchemasRef = v1.defineSchemas({
  SoftDeletableEntity: baseEntitySchemasRef.BaseEntity.extendWith({
    deletedAt: sharedPropsRef.dateTime.optional().nullable(),
  }),
}).ref;

export const auditedSoftDeletableEntitySchemasRef = v1.defineSchemas({
  AuditedSoftDeletableEntity: softDeletableEntitySchemasRef.SoftDeletableEntity.extendWith({
    createdBy: sharedPropsRef.uuid.optional().nullable(),
    updatedBy: sharedPropsRef.uuid.optional().nullable(),
  }),
}).ref;

export const baseSchemasRef = {
  ...baseEntitySchemasRef,
  ...softDeletableEntitySchemasRef,
  ...auditedSoftDeletableEntitySchemasRef,
} as const;
```

## Split Base Entities

Abstract base entities contribute field metadata only. They do not have stores.

```ts
export const baseEntityRef = v1.defineBaseEntities({
  BaseEntity: {
    kind: 'abstract',
    schema: baseEntitySchemasRef.BaseEntity,
    fields: {
      id: ($) => $.unique().index().role('primaryKey').generated('uuid').query((q) => q.exact()),
      createdAt: ($) => $.role('createdAt').readonly().managed().query((q) => q.date().range().sort()),
      updatedAt: ($) => $.role('updatedAt').readonly().managed().query((q) => q.date().range().sort()),
    },
  },
}).ref;

export const softDeletableEntityRef = v1.defineBaseEntities({
  SoftDeletableEntity: {
    kind: 'abstract',
    schema: softDeletableEntitySchemasRef.SoftDeletableEntity,
    extends: baseEntityRef.BaseEntity,
    fields: {
      deletedAt: ($) => $.role('softDelete').readonly().managed().query((q) => q.date().range()),
    },
  },
}).ref;

export const auditedSoftDeletableEntityRef = v1.defineBaseEntities({
  AuditedSoftDeletableEntity: {
    kind: 'abstract',
    schema: auditedSoftDeletableEntitySchemasRef.AuditedSoftDeletableEntity,
    extends: softDeletableEntityRef.SoftDeletableEntity,
    fields: {
      createdBy: ($) => $.role('auditActor').readonly().managed().query((q) => q.exact()),
      updatedBy: ($) => $.role('auditActor').readonly().managed().query((q) => q.exact()),
    },
  },
}).ref;

export const baseEntitiesRef = {
  ...baseEntityRef,
  ...softDeletableEntityRef,
  ...auditedSoftDeletableEntityRef,
} as const;
```

## Persistence-Clean Resource Schemas

Entity schemas should represent storage fields only. Public projection schemas may add nested relation arrays.

```ts
export const userSchemasRef = users.defineSchemas({
  User: baseSchemasRef.AuditedSoftDeletableEntity.extendWith({
    username: sharedPropsRef.username,
    status: userPropsRef.status,
    lastLoginAt: sharedPropsRef.dateTime.optional().nullable(),
  }),

  UserRole: baseSchemasRef.BaseEntity.extendWith({
    userId: sharedPropsRef.uuid,
    role: sharedPropsRef.roleName,
    status: userPropsRef.roleStatus,
  }),
}).ref;

export const userProjectionSchemasRef = users.defineSchemas({
  UserPublic: userSchemasRef.User.extendWith({
    roles: userSchemasRef.UserRole.array().optional(),
  }),

  UserPartial: userSchemasRef.User.partial(),
}).ref;
```

Use `userSchemasRef.User` as the entity schema. Use `userProjectionSchemasRef.UserPublic` for public output shapes.

## Resource Entities

```ts
export const userEntitiesRef = users.defineEntities({
  User: {
    schema: userSchemasRef.User,
    extends: baseEntitiesRef.AuditedSoftDeletableEntity,
    store: 'users',
    backend: {
      passwordHash: sharedPropsRef.token,
      refreshTokenHash: sharedPropsRef.token.optional().nullable(),
    },
    fields: {
      username: ($) =>
        $.unique()
          .index()
          .immutable()
          .query((q) => q.exact().search({ prefix: true, contains: true, fuzzy: true }).sort()),
      status: ($) => $.index().query((q) => q.exact().oneOf().sort()),
      lastLoginAt: ($) => $.readonly().managed().query((q) => q.date().range().sort()),
      passwordHash: ($) => $.index(),
      refreshTokenHash: ($) => $.index(),
    },
    constraints: (c) => ({
      uniq_user_username: c.unique(['username']),
      idx_user_status: c.index(['status']),
      chk_user_deleted_after_created: c.check(c.when(c.notNull('deletedAt'), c.gt('deletedAt', c.field('createdAt')))),
    }),
  },

  UserRole: {
    schema: userSchemasRef.UserRole,
    extends: baseEntitiesRef.BaseEntity,
    store: 'user_roles',
    fields: {
      userId: ($) => $.index().immutable().query((q) => q.exact()),
      role: ($) => $.index().query((q) => q.exact().oneOf()),
    },
  },
}).ref;
```

Backend fields are backend/storage-only. They are not public response fields, not selected by default, and not client-editable by default. Mention backend fields in `fields` only when adding metadata such as `index()` or query capability.

## Field Metadata

The `fields` block is for outliers and storage/query metadata.

Lifecycle helpers:

```ts
readonly()
managed()
immutable()
select(false)
edit(false)
```

Meanings:

```txt
readonly()     = client never writes this field
managed()      = backend/system owns the value; implies readonly behavior
immutable()    = settable on create, not updatable later
select(false)  = exclude from public/default selection metadata
edit(false)    = exclude from client-editable/update metadata
```

Query helpers:

```ts
q.exact()
q.oneOf()
q.range()
q.date()
q.search({ prefix: true, contains: true, fuzzy: true })
q.sort()
```

Query behavior is capability metadata only. Public query schemas remain explicit.

## Relations

Relations are topology metadata only. They do not imply public response nesting or public DTO generation.

```ts
users.defineEntityRelations({
  User: {
    roles: (r) => r.hasMany(userEntitiesRef.UserRole).local('id').foreign('userId'),
  },

  UserRole: {
    user: (r) => r.belongsTo(userEntitiesRef.User).local('userId').foreign('id').onDelete({ cascade: true }),
  },
});
```

Supported relation methods:

```ts
r.belongsTo(entityRef)
r.hasOne(entityRef)
r.hasMany(entityRef)
r.manyToMany(entityRef)
.local('localField')
.foreign('foreignField')
.onDelete({ cascade: true })
.onDelete({ restrict: true })
.onDelete({ setNull: true })
.onDelete({ noAction: true })
```

Only one `onDelete` option may be true.

## Constraints

Constraints use a neutral predicate vocabulary.

```ts
constraints: (c) => ({
  idx_user_status: c.index(['status']),
  uniq_user_username: c.unique(['username']),
  chk_user_deleted_after_created: c.check(
    c.when(
      c.notNull('deletedAt'),
      c.gt('deletedAt', c.field('createdAt')),
    ),
  ),
})
```

Supported predicate helpers:

```ts
c.gt(field, value)
c.gte(field, value)
c.lt(field, value)
c.lte(field, value)
c.eq(field, value)
c.neq(field, value)
c.notNull(field)
c.oneOf(field, values)
c.range(field, min, max)
c.when(condition, thenCondition)
c.and(...conditions)
c.or(...conditions)
c.field(fieldName)
```

## Public API Schemas Stay Explicit

Entity metadata never creates public query params. Define route query, body, and response schemas directly.

```ts
export const userQuerySchemasRef = users.defineSchemas({
  UserListQuery: transportSchemasRef.BaseQuery.extendWith({
    username: sharedPropsRef.username.optional(),
    status: userPropsRef.status.optional(),
  }),
}).ref;
```
