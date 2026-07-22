import { field, property } from '@/index';

import { schemas } from '../version';
import { primitives } from '../properties';
import { baseEntity } from './base.entity';

// ============================================================================
// TASK COMMENT ENTITY
// ============================================================================


export const taskComment = schemas
  .entity(
    'TaskComment',
    {
      task: field
        .relation()
        .required()
        .capability((c) => c.filter().select())
        .visibility((v) => v.internal()),

      author: field
        .relation()
        .required()
        .capability((c) => c.filter().select())
        .visibility((v) => v.internal()),

      body: field(primitives.ref.richText)
        .required()
        .visibility((v) => v.public()),

      // Inline enum on entity
      visibility: field(
        property.enum({
          public: { value: 'public', label: 'Public' },
          internal: { value: 'internal', label: 'Internal' },
        }),
      )
        .required()
        .capability((c) => c.filter())
        .visibility((v) => v.internal()),
    },
    {
      extends: baseEntity,
      tags: ['task_comment'],
      description: 'Task comment entity',
    },
  )
  .models({
    read: (m) => m.relations('expand'),
    create: (m) => m.omit('id', 'createdAt', 'updatedAt', 'deletedAt'),
    patch: (m) => m.partial().omit('id', 'createdAt', 'updatedAt', 'deletedAt'),
    public: (m) => m.pick('id', 'body', 'createdAt'),
    internal: (m) => m.pick('id', 'body', 'visibility', 'createdAt'),
  });
