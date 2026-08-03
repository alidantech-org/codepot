import { field } from '@/index';

import { schemas } from '../version';
import { primitives, enums, composites } from '../properties';
import { baseEntity } from './base.entity';

// ============================================================================
// TENANT ENTITY
// ============================================================================


export const tenant = schemas
  .entity(
    'Tenant',
    {
      ownerId: field(primitives.ref.id).capability((c) => c.filter()),

      name: field(primitives.ref.displayName)
        .required()
        .capability((c) => c.filter().sort().select())
        .visibility((v) => v.public()),
    },
    {
      extends: baseEntity,
      tags: ['tenant'],
    },
  )
  .models({
    public: (m) => m.pick('id', 'name'),
    create: (m) => m.omit('id', 'createdAt', 'updatedAt', 'deletedAt'),
    patch: (m) => m.partial().omit('id', 'createdAt', 'updatedAt', 'deletedAt'),
  });
