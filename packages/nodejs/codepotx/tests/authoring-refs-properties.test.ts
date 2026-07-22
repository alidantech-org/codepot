import assert from 'node:assert/strict';
import test from 'node:test';

import { RefKind, defineProperties, withRefMethods, z } from '../src/index';
import type {
  ComponentRef,
  PropertyRef,
  RefWithAccessAllowMethods,
  SchemaRefWithUsageMethods,
} from '../src/index';

test('defineProperties preserves typed refs and chained usage metadata', () => {
  const properties = defineProperties({ name: 'shared' }, 'User', {
    email: z.string().email(),
    status: z.enum(['active', 'disabled'] as const),
  });

  assert.equal(properties.ref.email.id, 'property:User:email');
  assert.equal(properties.ref.email.kind, RefKind.property);
  assert.equal(properties.ref.email.zod().safeParse('dev@alidantech.org').success, true);
  assert.equal(Object.keys(properties.ref.email).includes('optional'), false);

  const usage = properties.ref.email.optional().nullable().array();
  assert.deepEqual(usage.usage, { required: false, nullable: true, array: true });

  const allowed = (properties.ref.status as RefWithAccessAllowMethods<PropertyRef, 'active' | 'disabled'>)
    .allow({ active: true });
  assert.equal(allowed.source, properties.ref.status);
  assert.deepEqual(allowed.allow, { active: true });
});

test('resource-scoped properties preserve deterministic IDs and metadata', () => {
  const properties = defineProperties({
    name: 'users',
    resource: { name: 'users', alias: 'users', folders: ['platform'] },
  }, 'User', {
    name: z.string().min(1),
  });

  assert.equal(properties.ref.name.id, 'resource:users:property:User:name');
  assert.deepEqual(properties.ref.name.meta?.resource, { name: 'users', path: ['platform'] });
});

test('component refs preserve extension and projection chains', () => {
  const ref = withRefMethods<ComponentRef>({
    id: 'component:UserPublic',
    name: 'UserPublic',
    kind: RefKind.component,
    componentKey: 'UserPublic',
  });
  const schemaRef = ref as SchemaRefWithUsageMethods<ComponentRef, { id: unknown; name: unknown }>;

  const extension = schemaRef.extendWith({ avatar: { kind: 'field' } });
  assert.equal(extension.usage.extendWith !== undefined, true);
  assert.equal(extension.usage.composition?.base?.sourceRefId, ref.id);
  assert.equal(extension.usage.composition?.extensions?.[0]?.origin, 'inline');

  const projection = schemaRef.pick({ id: true, name: true }).partial();
  assert.deepEqual(projection.steps, [
    { mode: 'pick', fields: ['id', 'name'] },
    { mode: 'partial' },
  ]);

  assert.throws(
    () => (schemaRef.pick as (fields: Record<string, true | undefined>) => unknown)({ id: undefined }),
    /must be true/u,
  );
});
