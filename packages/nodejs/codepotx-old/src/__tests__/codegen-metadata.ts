import { strict as assert } from 'node:assert';
import { z } from 'zod';
import { CODEGEN_EXTENSION_KEY, HttpMethod, compileOpenApi, defineVersionContract } from '../index.js';

const v1 = defineVersionContract({
  info: {
    title: 'Codegen metadata',
    version: 'v1',
  },
});

const sharedProps = v1.defineProperties('Shared', {
  message: z.string(),
});

const users = v1.defineResource({
  name: 'users',
  route: '/users',
  folders: ['platform', 'users'],
});

const props = users.defineProperties('User', {
  id: z.string(),
  email: z.string().email(),
  status: z.enum(['active', 'suspended']),
});

const schemas = users.defineSchemas({
  UserQuery: {
    id: props.ref.id.optional(),
  },

  CreateUserBody: {
    email: props.ref.email,
  },

  UserOk: {
    id: props.ref.id,
    email: props.ref.email,
  },
});

users.defineRoutes({
  routes: {
    createUser: {
      method: HttpMethod.post,
      path: '/',
      query: schemas.ref.UserQuery,
      body: schemas.ref.CreateUserBody,
      responses: {
        201: schemas.ref.UserOk,
      },
    },
  },
});

const result = compileOpenApi(v1.contract, { validate: false });
assert.equal(result.success, true);

const userQuery = result.document.components.schemas.UserQuery as Record<string, unknown>;
const createUserBody = result.document.components.schemas.CreateUserBody as Record<string, unknown>;
const userOk = result.document.components.schemas.UserOk as Record<string, unknown>;
const sharedMessage = result.document.components.schemas.SharedMessage as Record<string, unknown>;
const userStatus = result.document.components.schemas.UserStatus as Record<string, unknown>;

assert.equal((userQuery[CODEGEN_EXTENSION_KEY] as { role?: string }).role, 'query');
assert.equal((createUserBody[CODEGEN_EXTENSION_KEY] as { role?: string }).role, 'body');
assert.equal((userOk[CODEGEN_EXTENSION_KEY] as { role?: string }).role, 'response');
assert.deepEqual(sharedMessage[CODEGEN_EXTENSION_KEY], {
  kind: 'primitive',
  shared: true,
});
assert.deepEqual(userStatus[CODEGEN_EXTENSION_KEY], {
  kind: 'enum',
  resource: {
    name: 'users',
    path: ['platform', 'users'],
  },
});
