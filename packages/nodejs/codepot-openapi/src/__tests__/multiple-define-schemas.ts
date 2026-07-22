import { strict as assert } from 'node:assert';
import { z } from 'zod';
import { compileOpenApi, defineVersionContract } from '../index.js';

const v1 = defineVersionContract({
  info: {
    title: 'Multiple schema calls',
    version: 'v1',
  },
});

const users = v1.defineResource({
  name: 'User',
  route: '/users',
});

const props = users.defineProperties('User', {
  id: z.string(),
});

const a = users.defineSchemas({
  A: {
    id: props.ref.id,
  },
});

const b = users.defineSchemas({
  B: {
    a: a.ref.A,
  },
});

users.defineSchemas({
  C: {
    a: users.schemas.ref.A,
    b: b.ref.B,
  },
});

assert.ok(users.schemas.ref.A);
assert.ok(users.schemas.ref.B);
assert.ok(users.schemas.ref.C);

assert.throws(
  () =>
    users.defineSchemas({
      A: {
        id: props.ref.id,
      },
    }),
  /Duplicate schema component "A"/,
);

const result = compileOpenApi(v1.contract, { validate: false });
assert.equal(result.success, true);
assert.ok(result.document.components.schemas.A);
assert.ok(result.document.components.schemas.B);
assert.ok(result.document.components.schemas.C);
