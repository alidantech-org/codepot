import { field } from '@/index';

import { schemas } from '../version';
import { baseEntity } from './base.entity';

// ============================================================================
// POST TAG ENTITY
// ============================================================================

export const postTag = schemas
  .entity(
    'PostTag',
    {
      post: field
        .relation()
        .required()
        .capability((c) => c.filter())
        .visibility((v) => v.internal()),

      tag: field
        .relation()
        .required()
        .capability((c) => c.filter())
        .visibility((v) => v.internal()),
    },
    {
      extends: baseEntity,
      tags: ['join', 'post_tag'],
    },
  )
  .models({
    read: (m) => m.relations('expand'),
    create: (m) => m.omit('id', 'createdAt', 'updatedAt', 'deletedAt'),
  });