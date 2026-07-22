import { strict as assert } from 'node:assert';
import { z } from 'zod';
import { CODEGEN_EXTENSION_KEY, compileOpenApi, defineVersionContract } from '../index.js';

const USER_ROLES = ['user', 'admin', 'super_admin', 'support'] as const;

const v1 = defineVersionContract({
  info: {
    title: 'Access metadata',
    version: 'v1',
  },
});

const sharedProps = v1.defineProperties('Shared', {
  uuid: z.string().uuid(),
  dateTime: z.string().datetime(),
  message: z.string(),
});

const authSchemas = v1.defineSchemas({
  AuthUserContext: {
    userId: sharedProps.ref.uuid,
  },

  RefreshTokenContext: {
    userId: sharedProps.ref.uuid,
    sessionId: sharedProps.ref.uuid,
  },
});

const baseAccess = v1.defineAccess({
  public: {
    context: null,
  },

  authenticated: {
    context: authSchemas.ref.AuthUserContext,
  },

  refreshToken: {
    context: authSchemas.ref.RefreshTokenContext,
    tags: ['refresh-token'],
  },
});

const users = v1.defineResource({
  name: 'users',
  route: '/auth/users',
  folders: ['auth'],
  ui: {
    enabled: true,
    infer: true,
  },
});

const userProps = users.defineProperties('User', {
  role: z.enum(USER_ROLES),
  username: z.string().min(1).max(100),
});

const objectAdmin = {
  context: authSchemas.ref.AuthUserContext,
  roles: {
    user: userProps.ref.role.allow({
      admin: true,
      super_admin: true,
    }),
  },
};

const builderAdmin = users.access
  .context(authSchemas.ref.AuthUserContext)
  .role('user', userProps.ref.role, {
    admin: true,
    super_admin: true,
  });

assert.deepEqual(builderAdmin.build(), objectAdmin);

const userAccess = users.defineAccess({
  admin: objectAdmin,

  adminViaBuilder: builderAdmin,

  superAdmin: users.access.context(authSchemas.ref.AuthUserContext).role('user', userProps.ref.role, {
    super_admin: true,
  }),
});

const apps = v1.defineResource({
  name: 'apps',
  route: '/platform/apps',
  folders: ['platform'],
  access: userAccess.ref.admin,
  ui: {
    enabled: true,
    infer: true,
  },
});

const appSchemas = apps.defineSchemas({
  AppRouteParams: {
    id: sharedProps.ref.uuid,
  },

  AppResponse: {
    id: sharedProps.ref.uuid,
    message: sharedProps.ref.message,
  },
});

apps
  .defineRoutes()
  .params(appSchemas.ref.AppRouteParams)
  .routes((r) => ({
    findApps: r.get('/').response(appSchemas.ref.AppResponse),

    deleteApp: r
      .delete('/:id')
      .access(userAccess.ref.superAdmin)
      .effects({
        cookies: {
          clear: ['access', 'refresh'],
        },
      })
      .tags(['platform', 'apps', 'dangerous', 'mutation'])
      .response(appSchemas.ref.AppResponse)
      .ui('delete'),

    findPublicApps: r.get('/public').access(baseAccess.ref.public).response(appSchemas.ref.AppResponse),

    refreshApps: r.post('/refresh').access(baseAccess.ref.refreshToken).response(appSchemas.ref.AppResponse),
  }));

assert.equal(baseAccess.ref.public.key, 'public');
assert.deepEqual(baseAccess.ref.public.owner, { global: true });
assert.equal(userAccess.ref.admin.key, 'admin');
assert.deepEqual(userAccess.ref.admin.owner, {
  resource: {
    name: 'users',
    path: ['auth'],
  },
});

const result = compileOpenApi(v1.contract, { validate: false });
assert.equal(result.success, true);
if (!result.success) {
  throw new Error('Expected compileOpenApi to succeed.');
}

const document = result.document;
const schemas = document.components.schemas as Record<string, Record<string, unknown>>;
const documentCodegen = document[CODEGEN_EXTENSION_KEY] as Record<string, unknown>;

function operation(path: string, method: string): Record<string, unknown> {
  const pathItem = document.paths[path] as Record<string, unknown> | undefined;
  assert.ok(pathItem, `Expected path ${path}`);

  const op = pathItem[method] as Record<string, unknown> | undefined;
  assert.ok(op, `Expected ${method.toUpperCase()} ${path}`);
  return op;
}

function codegen(path: string, method: string): Record<string, unknown> {
  const meta = operation(path, method)[CODEGEN_EXTENSION_KEY] as Record<string, unknown> | undefined;
  assert.ok(meta, `Expected x-codegen for ${method.toUpperCase()} ${path}`);
  return meta;
}

assert.ok(schemas.AuthUserContext);
assert.deepEqual((schemas.AuthUserContext[CODEGEN_EXTENSION_KEY] as Record<string, unknown>).role, 'context');
assert.deepEqual((schemas.UserRole[CODEGEN_EXTENSION_KEY] as Record<string, unknown>).role, 'access-role');
assert.deepEqual(schemas.SharedDateTime.type, 'string');
assert.deepEqual(schemas.SharedDateTime.format, 'date-time');
assert.deepEqual(((documentCodegen.resources as Record<string, Record<string, unknown>>).apps), {
  name: 'apps',
  path: ['platform'],
  route: '/platform/apps',
  tags: [],
  ui: {
    enabled: true,
    infer: true,
  },
});
assert.deepEqual(((document.paths['/platform/apps'] as Record<string, unknown>)[CODEGEN_EXTENSION_KEY] as Record<string, unknown>).resource, {
  $ref: '#/x-codegen/resources/apps',
});
assert.equal('resource' in codegen('/platform/apps', 'get'), false);

assert.deepEqual(codegen('/platform/apps', 'get').access, {
  $ref: '#/x-codegen/resources/users/access/admin',
});
assert.deepEqual(
  (((documentCodegen.resources as Record<string, Record<string, unknown>>).users.access as Record<string, Record<string, unknown>>).admin),
  {
    context: {
      $ref: '#/components/schemas/AuthUserContext',
    },
    roles: {
      user: {
        source: {
          $ref: '#/components/schemas/UserRole',
        },
        allow: {
          admin: true,
          super_admin: true,
        },
      },
    },
  },
);
assert.deepEqual((codegen('/platform/apps', 'get').ui as Record<string, unknown>).enabled, true);

assert.deepEqual(codegen('/platform/apps/{id}', 'delete').access, {
  $ref: '#/x-codegen/resources/users/access/superAdmin',
});
assert.deepEqual(codegen('/platform/apps/{id}', 'delete').tags, ['platform', 'apps', 'dangerous', 'mutation']);
assert.deepEqual(codegen('/platform/apps/{id}', 'delete').effects, {
  cookies: {
    clear: ['access', 'refresh'],
  },
});
assert.equal((document.paths['/platform/apps/{id}'] as { parameters?: unknown[] }).parameters, undefined);
assert.ok(Array.isArray(operation('/platform/apps/{id}', 'delete').parameters));

assert.deepEqual(codegen('/platform/apps/public', 'get').access, {
  $ref: '#/x-codegen/access/global/public',
});
assert.deepEqual(((documentCodegen.access as Record<string, unknown>).global as Record<string, unknown>).public, { context: null });
assert.deepEqual(operation('/platform/apps/public', 'get').security, []);

assert.deepEqual(codegen('/platform/apps/refresh', 'post').access, {
  $ref: '#/x-codegen/access/global/refreshToken',
});
assert.deepEqual(((documentCodegen.access as Record<string, unknown>).global as Record<string, unknown>).refreshToken, {
  context: {
    $ref: '#/components/schemas/RefreshTokenContext',
  },
  tags: ['refresh-token'],
});
assert.deepEqual(operation('/platform/apps/refresh', 'post').security, []);

const serialized = JSON.stringify(document);
assert.equal(serialized.includes('systemRoles'), false);
assert.equal(serialized.includes('tenantRoles'), false);
assert.equal(schemas.admin, undefined);
