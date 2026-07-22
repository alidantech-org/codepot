# codepot-openapi

TypeScript-first OpenAPI 3.1 contract builder with Zod-backed refs, route builders, JSON/YAML output, and compiler-resolved `x-codegen` metadata for generators.

## Install

```bash
pnpm add codepot-openapi zod
```

```bash
npm install codepot-openapi zod
```

`zod` is a peer dependency.

## Quick Start

```ts
import { ContentType, definePackageConfig, defineVersionContract } from 'codepot-openapi';
import { z } from 'zod';

export const v1 = defineVersionContract({
  info: {
    title: 'Example API',
    version: 'v1',
  },
  defaults: {
    requestContentType: ContentType.json,
    responseContentType: ContentType.json,
  },
});

export const sharedPropsRef = v1.defineProperties('Shared', {
  uuid: z.string().uuid(),
  dateTime: z.string().datetime(),
  username: z.string().min(1).max(100),
  token: z.string().min(1).max(500),
  boolean: z.boolean(),
  message: z.string().min(1).max(500),
}).ref;

export const baseEntitySchemasRef = v1.defineSchemas({
  BaseEntity: {
    id: sharedPropsRef.uuid,
    createdAt: sharedPropsRef.dateTime,
    updatedAt: sharedPropsRef.dateTime,
  },
}).ref;

export const auditedEntitySchemasRef = v1.defineSchemas({
  AuditedEntity: baseEntitySchemasRef.BaseEntity.extendWith({
    createdBy: sharedPropsRef.uuid.optional().nullable(),
    updatedBy: sharedPropsRef.uuid.optional().nullable(),
  }),
}).ref;

export const baseSchemasRef = {
  ...baseEntitySchemasRef,
  ...auditedEntitySchemasRef,
} as const;

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

export const auditedEntityRef = v1.defineBaseEntities({
  AuditedEntity: {
    kind: 'abstract',
    schema: auditedEntitySchemasRef.AuditedEntity,
    extends: baseEntityRef.BaseEntity,
    fields: {
      createdBy: ($) => $.role('auditActor').readonly().managed().query((q) => q.exact()),
      updatedBy: ($) => $.role('auditActor').readonly().managed().query((q) => q.exact()),
    },
  },
}).ref;

export const baseEntitiesRef = {
  ...baseEntityRef,
  ...auditedEntityRef,
} as const;

export const transportSchemasRef = v1.defineSchemas({
  ApiMessage: {
    message: sharedPropsRef.message,
  },
  BaseQuery: {
    search: sharedPropsRef.username.optional(),
  },
}).ref;

export const users = v1.defineResource({
  name: 'users',
  route: '/auth/users',
  folders: ['auth'],
  tags: ['admin', 'users'],
  ui: { enabled: true, infer: true },
});

export const userPropsRef = users.defineProperties('User', {
  status: z.enum(['active', 'suspended']).default('active'),
  roleStatus: z.enum(['active', 'revoked']).default('active'),
}).ref;

export const userSchemasRef = users.defineSchemas({
  User: baseSchemasRef.AuditedEntity.extendWith({
    username: sharedPropsRef.username,
    status: userPropsRef.status,
    lastLoginAt: sharedPropsRef.dateTime.optional().nullable(),
  }),

  UserRole: baseSchemasRef.BaseEntity.extendWith({
    userId: sharedPropsRef.uuid,
    role: sharedPropsRef.username,
    status: userPropsRef.roleStatus,
  }),
}).ref;

export const userEntitiesRef = users.defineEntities({
  User: {
    schema: userSchemasRef.User,
    extends: baseEntitiesRef.AuditedEntity,
    store: 'users',
    backend: {
      passwordHash: sharedPropsRef.token,
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
    },
    constraints: (c) => ({
      uniq_user_username: c.unique(['username']),
      idx_user_status: c.index(['status']),
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

users.defineEntityRelations({
  User: {
    roles: (r) => r.hasMany(userEntitiesRef.UserRole).local('id').foreign('userId'),
  },
  UserRole: {
    user: (r) => r.belongsTo(userEntitiesRef.User).local('userId').foreign('id').onDelete({ cascade: true }),
  },
});

export const userProjectionSchemasRef = users.defineSchemas({
  UserPublic: userSchemasRef.User.extendWith({
    roles: userSchemasRef.UserRole.array().optional(),
  }),
  UserPartial: userSchemasRef.User.partial(),
}).ref;

export const userQuerySchemasRef = users.defineSchemas({
  UserListQuery: transportSchemasRef.BaseQuery.extendWith({
    username: sharedPropsRef.username.optional(),
    status: userPropsRef.status.optional(),
  }),
}).ref;

export const userBodySchemasRef = users.defineSchemas({
  UpdateUserBody: userSchemasRef.User.pick({
    username: true,
    status: true,
  }).partial(),
}).ref;

export const userResponseSchemasRef = users.defineSchemas({
  UserResponse: {
    user: userProjectionSchemasRef.UserPublic,
  },
  UsersListResponse: {
    users: userProjectionSchemasRef.UserPartial.array(),
  },
}).ref;

export const userRoutes = users.defineRoutes().routes((r) => ({
  findUsers: r.get('/').query(userQuerySchemasRef.UserListQuery).response(userResponseSchemasRef.UsersListResponse).ui('list'),
  getUserById: r.get('/:id').response(userResponseSchemasRef.UserResponse).ui('detail'),
  updateUser: r
    .patch('/:id')
    .body(userBodySchemasRef.UpdateUserBody)
    .response(userResponseSchemasRef.UserResponse)
    .ui('update')
    .cache((c) => c.invalidate.on('findUsers').on('getUserById')),
}));

export default definePackageConfig({
  contracts: [v1],
  output: {
    folder: 'openapi',
    filePrefix: 'openapi',
    formats: ['json', 'yaml'],
  },
});
```

Generate files:

```bash
pnpm exec codepot-openapi generate
```

## Current API Shape

### Version Contracts

Use a version contract for one OpenAPI document. Shared properties, shared schemas, access policies, and abstract base entities can be defined directly on the version.

```ts
const v1 = defineVersionContract({
  info: {
    title: 'Example API',
    version: 'v1',
  },
});
```

### Resources

Resources own domain-specific properties, schemas, entities, access policies, hooks, and routes.

```ts
const users = v1.defineResource({
  name: 'users',
  route: '/users',
  folders: ['platform'],
  tags: ['platform', 'users'],
});
```

The compiler normalizes paths. Contracts may use `route: 'v1/users'` or `route: '/v1/users'`. Route params use `/:id` in contracts and compile to OpenAPI `{id}` params.

### Properties

`defineProperties(name, fields)` accepts a Zod map and returns reusable property refs.

```ts
const userPropsRef = users.defineProperties('User', {
  email: z.string().email(),
  status: z.enum(['active', 'suspended']),
}).ref;
```

Refs support usage helpers:

```ts
userPropsRef.email.optional()
userPropsRef.email.nullable()
userPropsRef.status.array()
```

### Schemas

Schemas are reusable DTO components. Multiple `defineSchemas()` calls merge into the resource or version schema registry.

```ts
const projectionsRef = users.defineSchemas({
  UserPreview: userSchemasRef.User.pick({
    id: true,
    username: true,
  }),
  UpdateUserBody: userSchemasRef.User.pick({
    username: true,
    status: true,
  }).partial(),
}).ref;
```

Projection helpers are `partial()`, `pick({ field: true })`, and `omit({ field: true })`. Projection chains preserve required fields correctly.

### Entities

Entity metadata is backend/storage-only. Entities derive from schemas, do not expose public query params, and do not create public DTO nesting. Public query, body, and response schemas remain explicit.

Best-practice order:

1. Define shared properties.
2. Define split base entity schemas.
3. Define split base entity metadata.
4. Define persistence-clean resource schemas.
5. Define resource entities from schemas.
6. Define entity relations.
7. Keep public query/body/response schemas explicit.

Field lifecycle helpers are:

```ts
readonly()
managed()
immutable()
select(false)
edit(false)
```

Normal fields are selectable, default-selected, creatable, and editable by default. The entity `fields` block is for metadata outliers.

Entity query capability helpers are:

```ts
q.exact()
q.oneOf()
q.range()
q.date()
q.search({ prefix: true, contains: true, fuzzy: true })
q.sort()
```

Query capability metadata does not create public route query schemas.

Backend-only fields belong under `backend`. They are backend/storage-only, not public response fields, not selected by default, and not client-editable by default.

Relations use entity refs and neutral topology metadata:

```ts
users.defineEntityRelations({
  UserRole: {
    user: (r) => r.belongsTo(userEntitiesRef.User).local('userId').foreign('id').onDelete({ cascade: true }),
  },
});
```

Supported relation methods are `belongsTo`, `hasOne`, `hasMany`, `manyToMany`, `local`, `foreign`, and `onDelete` with one of `{ cascade: true }`, `{ restrict: true }`, `{ setNull: true }`, or `{ noAction: true }`.

### Routes

Builder style:

```ts
users.defineRoutes().routes((r) => ({
  findUsers: r.get('/').query(userQuerySchemasRef.UserListQuery).response(userResponseSchemasRef.UsersListResponse).ui('list'),
  updateUser: r
    .patch('/:id')
    .body(userBodySchemasRef.UpdateUserBody)
    .response(userResponseSchemasRef.UserResponse)
    .ui('update')
    .cache((c) => c.invalidate.on('findUsers')),
}));
```

Route cache support is invalidation-only. `cache.invalidate.on(...)` takes an operation ID, and the compiler validates that the operation ID exists.

### Frontends

Frontends are explicit authoring constructs for future frontend generators. Resources and operations never create screens automatically. A screen or frontend component exists only when you define it.

Define components first, then screens reference component refs:

```ts
const adminFrontend = v1.defineFrontend({
  name: 'admin',
  title: 'Admin',
  routePrefix: '/admin',
  folders: ['admin'],
});

const adminComponentsRef = adminFrontend
  .defineComponents()
  .components((c) => ({
    AppsTable: c
      .component()
      .props({
        apps: appProjectionSchemasRef.AppPartial.array(),
      })
      .uses({
        findApps: appRoutes.ref.findApps,
      }),
  })).ref;

adminFrontend
  .defineScreens()
  .screens((s) => ({
    AppsListScreen: s
      .screen('/apps')
      .title('Apps')
      .uses({
        findApps: appRoutes.ref.findApps,
      })
      .components({
        table: adminComponentsRef.AppsTable,
      }),
  }));
```

Component props compile into normal `components.schemas` using deterministic names such as `AdminAppsTableProps`. Frontend metadata is emitted under root `x-codegen.frontends`, and a later generator can choose one frontend by name.

### Info Metadata

Use `info` for implementation guidance that generators, docs, and AI prompts can consume. It never changes runtime behavior.

```ts
const platformInfo = {
  apiKeySecurity: {
    security: [
      'Never store API keys in raw form.',
      'Expose only keyPrefix, never keyHash.',
    ],
    implement: ['Return the raw secret only once during creation.'],
  },
};

apps
  .info((i) =>
    i
      .explain('Platform apps resource.')
      .use(platformInfo.apiKeySecurity)
      .custom('tenantSafety', 'Always scope reads by tenant context.'),
  );

apps.defineRoutes().routes((r) => ({
  createApp: r
    .post('/')
    .response(appResponseSchemasRef.AppResponse)
    .info((i) => i.implement('Create app records transactionally.')),
}));
```

Info values compile under existing `x-codegen.info` locations as arrays of strings. Custom categories are allowed and duplicate messages are deduped.

### Runtime Hooks

Hooks are defined once on a resource and routes reference hook refs. Full hook definitions are emitted under `x-codegen.resources.<resource>.hooks`. Operation runtime hook usages are `$ref` pointers, so generators can resolve them without duplicated metadata.

```ts
const authHooksRef = auth.defineHooks({
  setSessionCookies: {
    phase: 'afterSuccess',
    transport: {
      outbound: {
        cookies: true,
      },
    },
    description: 'Set session cookies.',
  },
}).ref;

auth.defineRoutes().routes((r) => ({
  loginWithEmail: r.post('/login/email').runtime({
    transport: {
      outbound: {
        cookies: true,
      },
    },
    hooks: {
      afterSuccess: authHooksRef.setSessionCookies,
    },
  }),
}));
```

Supported phases are `beforeValidation`, `beforeHandler`, `afterSuccess`, `afterError`, and `afterSend`.

### UI Metadata

UI intent is resolved by the compiler and emitted under operation `x-codegen.ui`. `operation.role` is also preserved for generators.

```ts
ui: 'list'
ui: 'detail'
ui: 'create'
ui: 'update'
ui: 'delete'
ui: 'action'
ui: 'auth'
```

### Generated Metadata

Useful `x-codegen` metadata includes:

```txt
x-codegen.resources
x-codegen.frontends
x-codegen.baseEntities
x-codegen.entities
x-codegen.access
path.x-codegen.resource.$ref
operation.x-codegen.operation.name
operation.x-codegen.operation.role
operation.x-codegen.access.$ref
operation.x-codegen.runtime.hooks.<phase>[].$ref
operation.x-codegen.parameters.target
operation.x-codegen.cache.invalidate.operations
```

Resource, access, hook, and entity relation metadata use registry `$ref` pointers:

```yaml
x-codegen:
  resources:
    auth:
      name: auth
      path:
        - platform
      hooks:
        setSessionCookies:
          phase: afterSuccess
  access:
    global:
      public:
        context: null

paths:
  /auth/login:
    x-codegen:
      resource:
        $ref: '#/x-codegen/resources/auth'
    post:
      x-codegen:
        operation:
          name: loginWithEmail
          role: auth
        access:
          $ref: '#/x-codegen/access/global/public'
        runtime:
          hooks:
            afterSuccess:
              - $ref: '#/x-codegen/resources/auth/hooks/setSessionCookies'
```

Do not rename `parameters.target`, remove `operation.role`, or inline registry-backed metadata; those shapes are part of the accepted metadata contract.

### Content Types

```ts
ContentType.json
ContentType.multipartFormData
ContentType.formUrlEncoded
ContentType.octetStream
ContentType.textPlain
ContentType.textHtml
ContentType.pdf
ContentType.png
ContentType.jpeg
ContentType.webp
ContentType.svg
```

## CLI

```bash
codepot-openapi init
codepot-openapi generate
codepot-openapi validate
```

## Programmatic Usage

```ts
import { OpenApiTs, compileOpenApi, generateOpenApi, validateOpenApiDocument } from 'codepot-openapi';
```

## Publishing

```bash
pnpm install
pnpm typecheck
pnpm build
pnpm pack:dry
npm publish --access public
```

## Development

```bash
pnpm install
pnpm typecheck
pnpm build
pnpm dev
```

When using this package from another local project, rebuild after source changes because consumers load `dist`.
