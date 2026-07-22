# Examples

## Mini User Resource

This example assumes `sharedPropsRef`, `baseSchemasRef`, `baseEntitiesRef`, `transportSchemasRef`, and `sharedSchemasRef` are defined in shared contract files.

```ts
import { z } from 'zod';
import { v1 } from '../_global/version.contract.js';
import { baseEntitiesRef, baseSchemasRef, sharedPropsRef, sharedSchemasRef, transportSchemasRef } from '../_global/shared.contract.js';

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

export const userEntitiesRef = users.defineEntities({
  User: {
    schema: userSchemasRef.User,
    extends: baseEntitiesRef.AuditedSoftDeletableEntity,
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
    user: userSchemasRef.User,
  },

  UsersListResponse: sharedSchemasRef.PaginatedResponse.extendWith({
    users: userSchemasRef.User.partial().array(),
  }),
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
```

## Explicit Frontend Example

Resources and routes do not create frontend screens. Define frontend components and screens explicitly, and pass refs instead of string names.

```ts
export const adminFrontend = v1.defineFrontend({
  name: 'admin',
  title: 'Admin',
  routePrefix: '/admin',
  folders: ['admin'],
});

export const adminComponentsRef = adminFrontend
  .defineComponents()
  .components((c) => ({
    UsersTable: c
      .component()
      .props({
        users: userSchemasRef.User.partial().array(),
      })
      .uses({
        findUsers: userRoutes.ref.findUsers,
      }),
  })).ref;

export const adminScreensRef = adminFrontend
  .defineScreens()
  .screens((s) => ({
    UsersListScreen: s
      .screen('/users')
      .title('Users')
      .uses({
        findUsers: userRoutes.ref.findUsers,
      })
      .components({
        table: adminComponentsRef.UsersTable,
      }),
  })).ref;
```

## Reusable Info Example

```ts
export const platformInfo = {
  apiKeySecurity: {
    security: [
      'Never store API keys in raw form.',
      'Store only keyHash and expose only keyPrefix.',
    ],
    implement: ['Return the raw secret only once during key creation.'],
  },
};

export const apps = v1
  .defineResource({
    name: 'apps',
    route: '/platform/apps',
    info: {
      explain: 'Platform app management API.',
    },
  })
  .info((i) => i.custom('tenantSafety', 'Always scope app reads by tenant context.'));
```

## Runtime Hook Example

```ts
export const authHooksRef = auth.defineHooks({
  setSessionCookies: {
    phase: 'afterSuccess',
    transport: {
      outbound: {
        cookies: true,
      },
    },
    description: 'Set session cookies.',
  },

  auditFailedLogin: {
    phase: 'afterError',
    transport: {
      inbound: {
        ip: true,
        userAgent: true,
      },
    },
    description: 'Audit failed login attempts.',
  },
}).ref;

export const authRoutes = auth.defineRoutes().routes((r) => ({
  loginWithEmail: r.post('/login/email').runtime({
    transport: {
      inbound: {
        ip: true,
        userAgent: true,
      },
      outbound: {
        cookies: true,
      },
    },
    hooks: {
      afterSuccess: authHooksRef.setSessionCookies,
      afterError: authHooksRef.auditFailedLogin,
    },
  }),
}));
```
