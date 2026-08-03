import { field } from '@/index';

import { schemas } from '../version';
import { primitives, enums } from '../properties';
import { baseEntity } from './base.entity';

// ============================================================================
// AUDIT LOG ENTITY
// ============================================================================

export const auditLog = schemas
  .entity(
    'AuditLog',
    {
      user: field
        .relation()
        .optional()
        .capability((c) => c.filter().select())
        .visibility((v) => v.internal()),

      action: field(enums.ref.AuditAction)
        .required()
        .capability((c) => c.filter().sort())
        .visibility((v) => v.internal()),

      entityType: field(primitives.ref.shortText)
        .required()
        .capability((c) => c.filter())
        .visibility((v) => v.internal()),

      entityId: field(primitives.ref.id)
        .required()
        .capability((c) => c.filter())
        .visibility((v) => v.internal()),

      changes: field(primitives.ref.longText)
        .optional()
        .nullable()
        .visibility((v) => v.internal()),

      ipAddress: field(primitives.ref.ipAddress)
        .optional()
        .nullable()
        .visibility((v) => v.internal()),

      userAgent: field(primitives.ref.userAgent)
        .optional()
        .nullable()
        .visibility((v) => v.internal()),
    },
    {
      extends: baseEntity,
      tags: ['audit'],
      description: 'Audit log entity',
    },
  )
  .fieldSets({
    listSelect: (s) => s.only('id', 'action', 'entityType', 'entityId'),
    listSort: (s) => s.only('createdAt', 'action'),
    listFilter: (s) => s.only('id', 'action', 'entityType', 'entityId', 'user'),
  })
  .models({
    read: (m) => m.relations('expand'),
    create: (m) => m.omit('id', 'createdAt', 'updatedAt', 'deletedAt'),
    internal: (m) => m.pick('id', 'action', 'entityType', 'entityId', 'changes', 'ipAddress', 'userAgent'),
  });
