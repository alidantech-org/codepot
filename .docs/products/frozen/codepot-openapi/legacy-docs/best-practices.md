# Codepot Contract Authoring Guidelines

## 1. Export Refs Directly

Prefer exporting `.ref` values.

```ts
export const sharedPropsRef = v1.defineProperties('Shared', {
  uuid: z.string().uuid(),
  email: z.string().email(),
}).ref;
```

Avoid large contract objects that re-wrap registries. They make inferred public types larger and harder to name.

## 2. Use The `Ref` Suffix

Use names like:

```txt
sharedPropsRef
baseSchemasRef
transportSchemasRef
userPropsRef
userSchemasRef
userEntitiesRef
userRoutes
```

## 3. Keep Shared Items On The Version

Define global shared properties and schemas directly on the version contract.

```ts
export const transportSchemasRef = v1.defineSchemas({
  ApiMessage: {
    message: sharedPropsRef.message,
  },
}).ref;
```

## 4. Use Short Property Keys

Prefer concise property names:

```ts
uuid
dateTime
username
status
message
```

The generated schema names remain scoped by the property group.

## 5. Keep Entity Schemas Persistence-Clean

Entity schemas should represent storage fields. Public projection schemas can add relation arrays and API-only shapes.

```ts
export const userSchemasRef = users.defineSchemas({
  User: baseSchemasRef.AuditedSoftDeletableEntity.extendWith({
    username: sharedPropsRef.username,
    status: userPropsRef.status,
  }),
}).ref;
```

## 6. Define Base Schemas And Entities In Split Consts

Define `BaseEntity`, then later composed bases in separate calls. This keeps refs easy to reuse.

```ts
export const baseEntitySchemasRef = v1.defineSchemas({
  BaseEntity: {
    id: sharedPropsRef.uuid,
    createdAt: sharedPropsRef.dateTime,
    updatedAt: sharedPropsRef.dateTime,
  },
}).ref;
```

```ts
export const baseEntityRef = v1.defineBaseEntities({
  BaseEntity: {
    kind: 'abstract',
    schema: baseEntitySchemasRef.BaseEntity,
    fields: {
      id: ($) => $.unique().index().role('primaryKey').generated('uuid').query((q) => q.exact()),
    },
  },
}).ref;
```

## 7. Use Entity Field Metadata For Outliers

Normal fields are selectable, default-selected, creatable, and editable by default.

Use lifecycle helpers only when behavior differs:

```ts
fields: {
  username: ($) => $.unique().index().immutable().query((q) => q.exact().sort()),
  lastLoginAt: ($) => $.readonly().managed().query((q) => q.date().range().sort()),
  passwordHash: ($) => $.select(false).edit(false).index(),
}
```

## 8. Keep Public Query Schemas Explicit

Entity query behavior is capability metadata. It does not create public route query schemas.

```ts
export const userQuerySchemasRef = users.defineSchemas({
  UserListQuery: transportSchemasRef.BaseQuery.extendWith({
    username: sharedPropsRef.username.optional(),
    status: userPropsRef.status.optional(),
  }),
}).ref;
```

## 9. Use Projection-First Schemas

Use schema ref projections for public variants and mutable bodies.

```ts
export const userBodySchemasRef = users.defineSchemas({
  UpdateUserBody: userSchemasRef.User.pick({
    username: true,
    status: true,
  }).partial(),
}).ref;
```

## 10. Backend Fields Stay In `backend`

Backend-only fields are not public fields and are not client-editable by default.

```ts
backend: {
  passwordHash: sharedPropsRef.token,
}
```

Only add them to `fields` when they need metadata:

```ts
fields: {
  passwordHash: ($) => $.index(),
}
```

## 11. Use Neutral Relations

Relations use entity refs and neutral delete behavior objects.

```ts
users.defineEntityRelations({
  UserRole: {
    user: (r) => r.belongsTo(userEntitiesRef.User).local('userId').foreign('id').onDelete({ cascade: true }),
  },
});
```

## 12. Use Route Cache Invalidation By Operation ID

Route cache support is invalidation-only.

```ts
updateUser: r
  .patch('/:id')
  .response(userResponseSchemasRef.UserResponse)
  .cache((c) => c.invalidate.on('findUsers').on('getUserById')),
```

The compiler validates each operation ID.

## 13. Keep Route Definitions Clean

Use builder routes for fluent metadata:

```ts
export const userRoutes = users.defineRoutes().routes((r) => ({
  findUsers: r.get('/').query(userQuerySchemasRef.UserListQuery).response(userResponseSchemasRef.UsersListResponse).ui('list'),
  getUserById: r.get('/:id').response(userResponseSchemasRef.UserResponse).ui('detail'),
}));
```

## 14. Use Resource Tags

Resource tags are inherited by operation `x-codegen.tags`.

```ts
const users = v1.defineResource({
  name: 'users',
  route: '/auth/users',
  folders: ['auth'],
  tags: ['admin', 'users'],
});
```

## 15. Use Route Sources For Selectable Lists

Route sources describe which response array can drive generated selectors.

```ts
findUsers: r
  .get('/')
  .response(userResponseSchemasRef.UsersListResponse)
  .source('users', (user) => user.key('id').label('username')),
```

## 16. Define Hooks Once And Reference Them

Hooks are defined once. Routes attach hook refs.

```ts
export const authHooksRef = auth.defineHooks({
  setSessionCookies: {
    phase: 'afterSuccess',
    transport: {
      outbound: {
        cookies: true,
      },
    },
  },
}).ref;
```

## 17. Treat `x-codegen` As The Semantic Layer

Templates should read semantic metadata such as:

```txt
x-codegen.resources
x-codegen.frontends
x-codegen.baseEntities
x-codegen.entities
x-codegen.access
path.x-codegen.resource.$ref
operation.x-codegen.access.$ref
operation.x-codegen.runtime.hooks.<phase>[].$ref
operation.role
parameters.target
cache.invalidate.operations
```

Resource-owned definitions live in `x-codegen.resources`. Operation-level access and runtime hook usages are `$ref` pointers into the resource/global registries. Keep `operation.role` and `parameters.target` unchanged.

## 18. Author Frontends Explicitly

Do not infer frontend screens from backend resources or routes. Components and screens are frontend authoring constructs:

```ts
const adminFrontend = v1.defineFrontend({ name: 'admin' });

const adminComponentsRef = adminFrontend
  .defineComponents()
  .components((c) => ({
    UsersTable: c.component().uses({ findUsers: userRoutes.ref.findUsers }),
  })).ref;

adminFrontend.defineScreens().screens((s) => ({
  UsersListScreen: s.screen('/users').components({
      table: adminComponentsRef.UsersTable,
    }),
}));
```

Components should be defined before screens, and screens should reference component refs from the same frontend.

## 19. Use Info Metadata For Guidance

Use `info` for docs, generated comments, and implementation prompts. It should describe intent and constraints without changing runtime behavior.

```ts
const apiKeyInfo = {
  security: [
    'Never store API keys in raw form.',
    'Expose only keyPrefix, never keyHash.',
  ],
};

createAppApiKey: r
  .post('/:id/api-keys')
  .info((i) =>
    i
      .use(apiKeyInfo)
      .implement('Return the raw secret only once during key creation.'),
  ),
```

Custom categories are allowed:

```ts
.info((i) => i.custom('tenantSafety', 'Always scope reads by tenant context.'))
```

## 20. Export Only Reused Contract Parts

Export refs and route registries that other modules need. Local-only schemas can remain local.

```ts
const userBodySchemasRef = users.defineSchemas({
  UpdateUserBody: userSchemasRef.User.partial(),
}).ref;
```
