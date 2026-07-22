import { strict as assert } from 'node:assert';
import { z } from 'zod';
import { CODEGEN_EXTENSION_KEY, HttpMethod, compileOpenApi, defineVersionContract } from '../index.js';

const v1 = defineVersionContract({
  info: {
    title: 'Codegen UI metadata',
    version: 'v1',
  },
});

const sharedProps = v1.defineProperties('Shared', {
  id: z.string(),
  message: z.string(),
});

const users = v1.defineResource({
  name: 'users',
  route: 'v1/users',
  folders: ['platform'],
  ui: {
    enabled: true,
    infer: true,
  },
});

const auth = v1.defineResource({
  name: 'auth',
  route: '/v1/auth',
  folders: ['platform'],
  ui: {
    enabled: false,
  },
});

const adminAuth = v1.defineResource({
  name: 'adminAuth',
  route: '/v1/admin/auth',
  folders: ['platform'],
  ui: {
    enabled: true,
    infer: false,
  },
});

const bookings = v1.defineResource({
  name: 'bookings',
  route: '/v1/bookings',
  ui: {
    enabled: true,
    infer: false,
  },
});

const builderUsers = v1.defineResource({
  name: 'builderUsers',
  route: '/v1/builder-users',
});

const userSchemas = users.defineSchemas({
  UserRouteParams: {
    userId: sharedProps.ref.id,
  },
  UserBody: {
    message: sharedProps.ref.message,
  },
  UserOk: {
    id: sharedProps.ref.id,
    message: sharedProps.ref.message,
  },
});

const bookingSchemas = bookings.defineSchemas({
  BookingRouteParams: {
    bookingId: sharedProps.ref.id,
  },
  BookingOk: {
    id: sharedProps.ref.id,
    message: sharedProps.ref.message,
  },
});

const builderSchemas = builderUsers.defineSchemas({
  BuilderUserBody: {
    message: sharedProps.ref.message,
  },
  BuilderUserOk: {
    id: sharedProps.ref.id,
    message: sharedProps.ref.message,
  },
});

users.defineRoutes({
  params: userSchemas.ref.UserRouteParams,
  routes: {
    listUsers: {
      method: HttpMethod.get,
      path: '/',
      response: userSchemas.ref.UserOk,
    },
    createUser: {
      method: HttpMethod.post,
      path: '/',
      body: userSchemas.ref.UserBody,
      response: userSchemas.ref.UserOk,
      ui: {
        role: 'create',
      },
    },
    updateUser: {
      method: HttpMethod.patch,
      path: '/:userId',
      body: userSchemas.ref.UserBody,
      response: userSchemas.ref.UserOk,
    },
    exportUsers: {
      method: HttpMethod.get,
      path: '/export',
      response: userSchemas.ref.UserOk,
      ui: {
        enabled: false,
      },
    },
    cancelUser: {
      method: HttpMethod.post,
      path: '/:userId/cancel',
      response: userSchemas.ref.UserOk,
    },
    runUserAction: {
      method: HttpMethod.post,
      path: '/:userId/run-action',
      response: userSchemas.ref.UserOk,
      ui: 'action',
    },
  },
});

auth.defineRoutes({
  routes: {
    login: {
      method: HttpMethod.post,
      path: '/login',
      body: userSchemas.ref.UserBody,
      response: userSchemas.ref.UserOk,
    },
  },
});

adminAuth.defineRoutes({
  routes: {
    adminLogin: {
      method: HttpMethod.post,
      path: '/login',
      body: userSchemas.ref.UserBody,
      response: userSchemas.ref.UserOk,
      ui: 'auth',
    },
  },
});

bookings.defineRoutes({
  params: bookingSchemas.ref.BookingRouteParams,
  routes: {
    listBookings: {
      method: HttpMethod.get,
      path: '/',
      response: bookingSchemas.ref.BookingOk,
    },
    cancelBooking: {
      method: HttpMethod.post,
      path: '/:bookingId/cancel',
      response: bookingSchemas.ref.BookingOk,
      ui: {
        role: 'action',
      },
    },
  },
});

builderUsers.defineRoutes().routes((b) => ({
  builderListUsers: b.get('/').response(builderSchemas.ref.BuilderUserOk).ui('list'),
  builderCreateUser: b.post('/').body(builderSchemas.ref.BuilderUserBody).response(builderSchemas.ref.BuilderUserOk).ui({ role: 'create' }),
}));

const result = compileOpenApi(v1.contract, { validate: false });
assert.equal(result.success, true);
if (!result.success) {
  throw new Error('Expected compileOpenApi to succeed.');
}
const document = result.document;

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

assert.deepEqual(codegen('/v1/users', 'get').ui, {
  enabled: true,
  role: 'list',
  inferred: true,
  inferenceSource: 'compiler',
  inferenceReason: 'GET collection route',
});
assert.deepEqual(((document.paths['/v1/users'] as Record<string, unknown>)[CODEGEN_EXTENSION_KEY] as Record<string, unknown>).resource, {
  $ref: '#/x-codegen/resources/users',
});
assert.equal('resource' in codegen('/v1/users', 'get'), false);
assert.deepEqual(codegen('/v1/users', 'get').operation, {
  name: 'listUsers',
  role: 'list',
});

assert.deepEqual(codegen('/v1/users', 'post').ui, {
  enabled: true,
  role: 'create',
  inferred: false,
});
assert.deepEqual(codegen('/v1/users/{userId}', 'patch').ui, {
  enabled: true,
  role: 'update',
  inferred: true,
  inferenceSource: 'compiler',
  inferenceReason: 'PATCH item route',
});
assert.deepEqual(codegen('/v1/users/export', 'get').ui, {
  enabled: false,
});
assert.deepEqual(codegen('/v1/users/{userId}/cancel', 'post').ui, {
  enabled: false,
});
assert.deepEqual(codegen('/v1/users/{userId}/run-action', 'post').ui, {
  enabled: true,
  role: 'action',
  inferred: false,
});
assert.deepEqual(codegen('/v1/auth/login', 'post').ui, {
  enabled: false,
});
assert.deepEqual(((document.paths['/v1/admin/auth/login'] as Record<string, unknown>)[CODEGEN_EXTENSION_KEY] as Record<string, unknown>).resource, {
  $ref: '#/x-codegen/resources/adminAuth',
});
assert.equal('resource' in codegen('/v1/admin/auth/login', 'post'), false);
assert.deepEqual(codegen('/v1/admin/auth/login', 'post').operation, {
  name: 'adminLogin',
  role: 'auth',
});
assert.deepEqual(codegen('/v1/admin/auth/login', 'post').ui, {
  enabled: true,
  role: 'auth',
  inferred: false,
});
assert.deepEqual(codegen('/v1/bookings', 'get').ui, {
  enabled: false,
});
assert.deepEqual(codegen('/v1/bookings/{bookingId}/cancel', 'post').ui, {
  enabled: true,
  role: 'action',
  inferred: false,
});
assert.deepEqual(codegen('/v1/builder-users', 'get').ui, {
  enabled: true,
  role: 'list',
  inferred: false,
});
assert.deepEqual(codegen('/v1/builder-users', 'post').ui, {
  enabled: true,
  role: 'create',
  inferred: false,
});
