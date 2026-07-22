import { field } from '@/index';

import { schemas } from '../version';
import { primitives } from '../properties';
import { baseEntity } from './base.entity';

// ============================================================================
// PROFILE ENTITY
// ============================================================================

export const profile = schemas
  .entity(
    'Profile',
    {
      user: field
        .relation()
        .required()
        .capability((c) => c.filter().select())
        .visibility((v) => v.internal()),

      tenantSnapshot: field
        .relation()
        .optional()
        .visibility((v) => v.internal()),

      displayName: field(primitives.ref.displayName)
        .required()
        .visibility((v) => v.public()),

      bio: field(primitives.ref.bio)
        .optional()
        .nullable()
        .visibility((v) => v.public()),
    },
    { extends: baseEntity },
  )
  .models({
    public: (m) => m.pick('id', 'displayName', 'bio'),
    create: (m) => m.omit('id', 'createdAt', 'updatedAt', 'deletedAt', 'user', 'tenantSnapshot'),
    patch: (m) => m.partial().omit('id', 'createdAt', 'updatedAt', 'deletedAt'),
  });