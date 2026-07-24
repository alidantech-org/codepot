import assert from 'node:assert/strict';
import { z } from 'zod';
import { CODEGEN_EXTENSION_KEY } from '../codegen/codegen-extension.keys.js';
import { compileOpenApi } from '../compiler/compile-openapi.js';
import { defineVersionContract } from '../version/define-version-contract.js';

const v1 = defineVersionContract({
  info: {
    title: 'Entity metadata',
    version: 'v1',
  },
});

const sharedProps = v1.defineProperties('Shared', {
  uuid: z.string().uuid(),
  dateTime: z.string().datetime(),
  token: z.string(),
  username: z.string().min(3),
  status: z.enum(['active', 'pending', 'disabled']),
  boolean: z.boolean(),
});

const baseSchemas = v1.defineSchemas({
  BaseEntity: {
    id: sharedProps.ref.uuid,
    createdAt: sharedProps.ref.dateTime,
    updatedAt: sharedProps.ref.dateTime,
  },
});

const composedBaseSchemas = v1.defineSchemas({
  SoftDeletableEntity: baseSchemas.ref.BaseEntity.extendWith({
    deletedAt: sharedProps.ref.dateTime.optional().nullable(),
  }),
});

const baseEntities = v1.defineBaseEntities((base) => ({
  BaseEntity: {
    kind: 'abstract',
    schema: baseSchemas.ref.BaseEntity,
    fields: {
      id: ($) => $.unique().index().role('primaryKey').generated('uuid').query((q) => q.exact()),
      createdAt: ($) => $.role('createdAt').query((q) => q.date().range().sort()),
      updatedAt: ($) => $.role('updatedAt').query((q) => q.date().range().sort()),
    },
  },

  SoftDeletableEntity: {
    kind: 'abstract',
    schema: composedBaseSchemas.ref.SoftDeletableEntity,
    extends: base.ref.BaseEntity,
    fields: {
      deletedAt: ($) => $.role('softDelete').query((q) => q.date().range()),
    },
  },
}));

const users = v1.defineResource({
  name: 'users',
  route: '/users',
  folders: ['auth'],
});

const userProps = users.defineProperties('User', {
  role: z.enum(['owner', 'admin', 'member']),
});

const userSchemas = users.defineSchemas({
  User: composedBaseSchemas.ref.SoftDeletableEntity.extendWith({
    username: sharedProps.ref.username,
    status: sharedProps.ref.status,
    isActive: sharedProps.ref.boolean,
  }),

  UserRole: baseSchemas.ref.BaseEntity.extendWith({
    userId: sharedProps.ref.uuid,
    role: userProps.ref.role,
  }),
});

const userEntities = users.defineEntities({
  User: {
    schema: userSchemas.ref.User,
    extends: baseEntities.ref.SoftDeletableEntity,
    store: 'users',
    backend: {
      passwordHash: sharedProps.ref.token,
    },
    fields: {
      username: ($) =>
        $.unique()
          .index()
          .query((q) =>
            q
              .exact()
              .search({
                prefix: true,
                contains: true,
                fuzzy: true,
              })
              .sort(),
          ),
      status: ($) => $.index().query((q) => q.exact().oneOf().sort()),
      isActive: ($) => $.readonly().managed().query((q) => q.exact()),
      deletedAt: ($) => $.immutable(),
      passwordHash: ($) => $.index(),
    },
    constraints: (c) => ({
      idx_user_status: c.index(['status']),
      uniq_user_username: c.unique(['username']),
      chk_user_deleted_after_created: c.check(c.when(c.notNull('deletedAt'), c.gt('deletedAt', c.field('createdAt')))),
    }),
  },

  UserRole: {
    schema: userSchemas.ref.UserRole,
    extends: baseEntities.ref.BaseEntity,
    store: 'user_roles',
    fields: {
      userId: ($) => $.index().query((q) => q.exact()),
      role: ($) => $.index().query((q) => q.exact().oneOf()),
    },
  },
});

users.defineEntityRelations({
  User: {
    roles: (r) => r.hasMany(userEntities.ref.UserRole).local('id').foreign('userId').onDelete({ cascade: true }),
  },
  UserRole: {
    user: (r) => r.belongsTo(userEntities.ref.User).local('userId').foreign('id').onDelete({ restrict: true }),
  },
});

users
  .defineRoutes()
  .routes((r) => ({
    findUsers: r.get('/').response(userSchemas.ref.User).cache((c) => c.invalidate.on('updateUser').on('deleteUser')),
    updateUser: r.patch('/:id').response(userSchemas.ref.User),
    deleteUser: r.delete('/:id').response(userSchemas.ref.User),
  }));

const result = compileOpenApi(v1.contract);
assert.equal(result.success, true);

const documentCodegen = result.document[CODEGEN_EXTENSION_KEY] as Record<string, unknown>;
const baseEntityMetadata = documentCodegen.baseEntities as Record<string, Record<string, unknown>>;
const entityGroups = documentCodegen.entities as Record<string, Record<string, Record<string, unknown>>>;
const userEntity = entityGroups.users.User;

assert.equal(baseEntityMetadata.BaseEntity.kind, 'abstract');
assert.equal(baseEntityMetadata.BaseEntity.store, undefined);
assert.deepEqual(baseEntityMetadata.SoftDeletableEntity.extends, {
  owner: { global: true },
  key: 'BaseEntity',
});

assert.equal(userEntity.kind, 'entity');
assert.equal(userEntity.store, 'users');
assert.deepEqual(userEntity.resource, { $ref: '#/x-codegen/resources/users' });
assert.deepEqual(userEntity.visibility, ['backend', 'storage']);
assert.deepEqual(userEntity.extends, {
  owner: { global: true },
  key: 'SoftDeletableEntity',
});

const fields = userEntity.fields as Record<string, Record<string, unknown>>;
assert.equal(fields.id.role, 'primaryKey');
assert.equal(fields.deletedAt.immutable, true);
assert.equal(fields.username.unique, true);
assert.equal(fields.isActive.readonly, true);
assert.equal(fields.isActive.managed, true);
assert.equal(fields.isActive.edit, false);
assert.deepEqual((fields.username.query as Record<string, unknown>).search, {
  prefix: true,
  contains: true,
  fuzzy: true,
});
assert.equal((fields.status.query as Record<string, unknown>).oneOf, true);

const backend = userEntity.backend as Record<string, unknown>;
assert.deepEqual(backend.passwordHash, { $ref: '#/components/schemas/SharedToken' });
assert.equal((result.document.components.schemas.User as Record<string, unknown>).passwordHash, undefined);
assert.equal(fields.passwordHash.select, false);
assert.equal(fields.passwordHash.edit, false);
assert.equal(fields.username.select, undefined);
assert.equal(fields.username.edit, undefined);
assert.equal(Object.prototype.hasOwnProperty.call(fields, 'createdAt'), true);
assert.equal(Object.prototype.hasOwnProperty.call(fields, 'updatedAt'), true);

assert.deepEqual((userEntity.relations as Record<string, unknown>).roles, {
  cardinality: 'hasMany',
  target: {
    $ref: '#/x-codegen/entities/users/UserRole',
  },
  local: 'id',
  foreign: 'userId',
  onDelete: {
    cascade: true,
  },
});

const findUsersOperation = (result.document.paths['/users'] as Record<string, unknown>).get as Record<string, unknown>;
assert.deepEqual(((findUsersOperation['x-codegen'] as Record<string, unknown>).cache as Record<string, unknown>), {
  invalidate: {
    operations: ['updateUser', 'deleteUser'],
  },
});

assert.deepEqual(((userEntity.constraints as Record<string, Record<string, unknown>>).chk_user_deleted_after_created.rule as Record<string, unknown>).then, {
  op: 'gt',
  field: 'deletedAt',
  value: {
    $field: 'createdAt',
  },
});

const serializedUserEntity = JSON.stringify(userEntity);
assert.equal(serializedUserEntity.includes('systemManaged'), false);
assert.equal(serializedUserEntity.includes('frozenAfterCreate'), false);

assert.throws(
  () =>
    v1.defineEntities({
      BadSearch: {
        schema: baseSchemas.ref.BaseEntity,
        store: 'bad_search',
        fields: {
          id: ($) => $.query((q) => q.search({})),
        },
      },
    }),
  /requires at least one true option/,
);

assert.equal(typeof (createEntityFieldProbe() as unknown as { systemManaged?: unknown }).systemManaged, 'undefined');
assert.equal(typeof (createEntityFieldProbe() as unknown as { frozenAfterCreate?: unknown }).frozenAfterCreate, 'undefined');

assert.throws(
  () =>
    users.defineEntityRelations({
      User: {
        badDelete: (r) => r.belongsTo(userEntities.ref.UserRole).local('id').foreign('userId').onDelete({ cascade: true, restrict: true }),
      },
    }),
  /requires exactly one true option/,
);

const invalidCache = defineVersionContract({
  info: {
    title: 'Invalid cache',
    version: 'v1',
  },
});
const invalidCacheResource = invalidCache.defineResource({ name: 'invalid', route: '/invalid' });
invalidCacheResource.defineRoutes().routes((r) => ({
  one: r.get('/').cache((c) => c.invalidate.on('missingOperation')),
}));
assert.throws(() => compileOpenApi(invalidCache.contract), /Operation "one" invalidates unknown operation "missingOperation"/);

const splitBaseContract = defineVersionContract({
  info: {
    title: 'Split base entities',
    version: 'v1',
  },
});
const splitProps = splitBaseContract.defineProperties('Shared', {
  uuid: z.string().uuid(),
  dateTime: z.string().datetime(),
}).ref;
const splitBaseSchemas = splitBaseContract.defineSchemas({
  BaseEntity: {
    id: splitProps.uuid,
    createdAt: splitProps.dateTime,
    updatedAt: splitProps.dateTime,
  },
}).ref;
const splitSoftSchemas = splitBaseContract.defineSchemas({
  SoftDeletableEntity: splitBaseSchemas.BaseEntity.extendWith({
    deletedAt: splitProps.dateTime.optional().nullable(),
  }),
}).ref;
const splitBaseEntities = splitBaseContract.defineBaseEntities({
  BaseEntity: {
    kind: 'abstract',
    schema: splitBaseSchemas.BaseEntity,
    fields: {
      id: ($) => $.unique().index().role('primaryKey').query((q) => q.exact()),
    },
  },
}).ref;
splitBaseContract.defineBaseEntities({
  SoftDeletableEntity: {
    kind: 'abstract',
    schema: splitSoftSchemas.SoftDeletableEntity,
    extends: splitBaseEntities.BaseEntity,
    fields: {
      deletedAt: ($) => $.role('softDelete').readonly().managed().query((q) => q.date().range()),
    },
  },
});
const splitResult = compileOpenApi(splitBaseContract.contract);
assert.equal(splitResult.success, true);
assert.equal(
  (((splitResult.document[CODEGEN_EXTENSION_KEY] as Record<string, unknown>).baseEntities as Record<string, Record<string, unknown>>).BaseEntity.fields as Record<string, unknown>).id !==
    undefined,
  true,
);
assert.equal(
  Object.prototype.hasOwnProperty.call(
    ((splitResult.document[CODEGEN_EXTENSION_KEY] as Record<string, unknown>).baseEntities as Record<string, Record<string, Record<string, unknown>>>).BaseEntity.fields,
    'createdAt',
  ),
  false,
);

console.log('entity-metadata tests passed');

function createEntityFieldProbe() {
  let probe: unknown;
  v1.defineEntities({
    Probe: {
      schema: baseSchemas.ref.BaseEntity,
      store: 'probe',
      fields: {
        id: ($) => {
          probe = $;
          return $.index();
        },
      },
    },
  });
  return probe;
}
