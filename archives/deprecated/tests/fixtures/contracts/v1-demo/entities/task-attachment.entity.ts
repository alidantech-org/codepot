import { field, property } from '@/index';

import { schemas } from '../version';
import { composites } from '../properties';
import { baseEntity } from './base.entity';

// ============================================================================
// TASK ATTACHMENT ENTITY
// ============================================================================

export const taskAttachment = schemas
  .entity(
    'TaskAttachment',
    {
      task: field
        .relation()
        .required()
        .capability((c) => c.filter().select())
        .visibility((v) => v.internal()),

      uploadedBy: field
        .relation()
        .required()
        .capability((c) => c.filter().select())
        .visibility((v) => v.internal()),

      file: field(composites.ref.fileAsset)
        .required()
        .visibility((v) => v.public()),

      // Inline enum on entity
      status: field(
        property.enum({
          pending: { value: 'pending', label: 'Pending' },
          processing: { value: 'processing', label: 'Processing' },
          completed: { value: 'completed', label: 'Completed' },
          failed: { value: 'failed', label: 'Failed' },
        }),
      )
        .required()
        .capability((c) => c.filter())
        .visibility((v) => v.internal()),
    },
    {
      extends: baseEntity,
      tags: ['task_attachment'],
      description: 'Task attachment entity',
    },
  )
  .models({
    read: (m) => m.relations('expand'),
    create: (m) => m.omit('id', 'createdAt', 'updatedAt', 'deletedAt'),
    patch: (m) => m.partial().omit('id', 'createdAt', 'updatedAt', 'deletedAt'),
    public: (m) => m.pick('id', 'file', 'createdAt'),
    internal: (m) => m.pick('id', 'file', 'status', 'createdAt'),
  });
