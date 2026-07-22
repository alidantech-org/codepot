import { strict as assert } from 'node:assert';
import { z } from 'zod';
import { CODEGEN_EXTENSION_KEY, HttpMethod, compileOpenApi, defineVersionContract } from '../index.js';

const v1 = defineVersionContract({
  info: {
    title: 'Route Builder Pattern API',
    version: 'v1',
  },
  tags: ['v1', 'auth'],
});

const sharedProps = v1.defineProperties('Shared', {
  uuid: z.string().uuid(),
  message: z.string(),
});

const users = v1.defineResource({
  name: 'users',
  route: '/users',
  folders: ['auth'],
  tags: ['auth', 'users', 'admin'],
  ui: {
    enabled: true,
    infer: true,
  },
});

const userProps = users.defineProperties('User', {
  username: z.string().min(1),
});

const userSchemas = users.defineSchemas({
  UserRouteParams: {
    id: sharedProps.ref.uuid,
    roleId: sharedProps.ref.uuid,
  },

  UserPartial: {
    id: sharedProps.ref.uuid,
    username: userProps.ref.username,
  },

  UserListQuery: {
    search: sharedProps.ref.message.optional(),
  },

});

const responseSchemas = users.defineSchemas({
  UsersListOk: {
    users: userSchemas.ref.UserPartial.array(),
  },

  UserOk: {
    user: userSchemas.ref.UserPartial,
  },
});

const userRoutes = users
  .defineRoutes()
  .params(userSchemas.ref.UserRouteParams)
  .routes((r) => ({
    findUsers: r
      .get('/')
      .query(userSchemas.ref.UserListQuery)
      .response(responseSchemas.ref.UsersListOk)
      .source('users', (user) => user.key('id').label('username'))
      .tags(['list', 'admin'])
      .ui('list'),

    getUserById: r
      .get('/:id')
      .response(responseSchemas.ref.UserOk)
      .tags(['detail'])
      .ui('detail'),

    updateUserRole: r
      .patch('/:id/roles/:roleId')
      .response(responseSchemas.ref.UserOk)
      .tags(['mutation'])
      .ui('update'),
  }));

const tickets = v1.defineResource({
  name: 'tickets',
  route: '/tickets',
  folders: ['support'],
  tags: ['support', 'tickets'],
});

const ticketSchemas = tickets.defineSchemas({
  TicketRouteParams: {
    id: sharedProps.ref.uuid,
  },

  CreateTicketBody: {
    createdByUserId: sharedProps.ref.uuid.source(userRoutes.ref.findUsers),
    assignedToUserId: sharedProps.ref.uuid.source(userRoutes.ref.findUsers.sources.users),
  },

  TicketResponse: {
    id: sharedProps.ref.uuid,
  },
});

tickets.defineRoutes({
  params: ticketSchemas.ref.TicketRouteParams,
  routes: {
    createTicket: {
      method: HttpMethod.post,
      path: '/',
      body: ticketSchemas.ref.CreateTicketBody,
      response: ticketSchemas.ref.TicketResponse,
      tags: ['mutation'],
      ui: 'create',
    },

    getTicket: {
      method: HttpMethod.get,
      path: '/:id',
      response: ticketSchemas.ref.TicketResponse,
      tags: ['detail'],
      ui: 'detail',
    },
  },
});

assert.equal(userRoutes.ref.findUsers.routeKey, 'findUsers');
assert.equal(userRoutes.ref.findUsers.method, HttpMethod.get);
assert.ok(userRoutes.ref.findUsers.sources.users);
assert.equal(userRoutes.routes.findUsers.operationId, 'findUsers');

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

assert.equal(operation('/users', 'get').operationId, 'findUsers');
assert.equal(operation('/users/{id}', 'get').operationId, 'getUserById');
assert.equal(operation('/users/{id}/roles/{roleId}', 'patch').operationId, 'updateUserRole');

assert.equal((document.paths['/users/{id}'] as { parameters?: unknown[] }).parameters, undefined);
assert.ok(JSON.stringify(operation('/users/{id}', 'get').parameters).includes('UsersIdPathParam'));
assert.ok(JSON.stringify(operation('/users/{id}/roles/{roleId}', 'patch').parameters).includes('UsersIdPathParam'));
assert.ok(JSON.stringify(operation('/users/{id}/roles/{roleId}', 'patch').parameters).includes('UsersRoleIdPathParam'));

assert.deepEqual(codegen('/users', 'get').sources, {
  users: {
    responseField: 'users',
    item: {
      $ref: '#/components/schemas/UserPartial',
    },
    key: 'id',
    label: 'username',
  },
});
assert.deepEqual(codegen('/users', 'get').tags, ['v1', 'auth', 'users', 'admin', 'list']);
assert.deepEqual(operation('/users', 'get').tags, ['users']);
assert.deepEqual((codegen('/users', 'get').ui as Record<string, unknown>).role, 'list');
assert.deepEqual(((document.paths['/users'] as Record<string, unknown>)[CODEGEN_EXTENSION_KEY] as Record<string, unknown>).resource, {
  $ref: '#/x-codegen/resources/users',
});
assert.equal('resource' in codegen('/users', 'get'), false);
assert.deepEqual((codegen('/users', 'get').operation as Record<string, unknown>).name, 'findUsers');

const createTicketBody = document.components.schemas.CreateTicketBody as {
  properties: Record<string, Record<string, unknown>>;
};
assert.deepEqual(createTicketBody.properties.createdByUserId[CODEGEN_EXTENSION_KEY], {
  source: {
    kind: 'route',
    resource: {
      name: 'users',
      path: ['auth'],
    },
    operationId: 'findUsers',
    source: 'users',
    responseField: 'users',
    key: 'id',
    label: 'username',
  },
});
assert.deepEqual(createTicketBody.properties.assignedToUserId[CODEGEN_EXTENSION_KEY], createTicketBody.properties.createdByUserId[CODEGEN_EXTENSION_KEY]);

assert.equal((document.paths['/tickets/{id}'] as { parameters?: unknown[] }).parameters, undefined);
assert.ok(JSON.stringify(operation('/tickets/{id}', 'get').parameters).includes('TicketsIdPathParam'));
assert.deepEqual(codegen('/tickets/{id}', 'get').tags, ['v1', 'auth', 'support', 'tickets', 'detail']);
assert.deepEqual(operation('/tickets/{id}', 'get').tags, ['tickets']);
