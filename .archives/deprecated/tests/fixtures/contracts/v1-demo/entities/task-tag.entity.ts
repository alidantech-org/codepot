import { field } from '@/index';

import { schemas } from '../version';
import { baseEntity } from './base.entity';

// ============================================================================
// TASK TAG ENTITY
// ============================================================================

export const taskTag = schemas
  .entity(
    'TaskTag',
    {
      task: field
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
      tags: ['join', 'task_tag'],
    },
  )
  .models({
    read: (m) => m.relations('expand'),
    create: (m) => m.omit('id', 'createdAt', 'updatedAt', 'deletedAt'),
  });