import { field } from '@/index';

import { schemas } from '../version';
import { primitives, enums } from '../properties';
import { baseEntity } from './base.entity';

// ============================================================================
// NOTIFICATION ENTITY
// ============================================================================


export const notification = schemas
  .entity(
    'Notification',
    {
      user: field
        .relation()
        .required()
        .capability((c) => c.filter().select())
        .visibility((v) => v.internal()),

      channel: field(enums.ref.NotificationChannel)
        .required()
        .capability((c) => c.filter())
        .visibility((v) => v.internal()),

      title: field(primitives.ref.title)
        .required()
        .visibility((v) => v.public()),

      body: field(primitives.ref.message)
        .required()
        .visibility((v) => v.public()),

      readAt: field(primitives.ref.dateTime)
        .optional()
        .nullable()
        .capability((c) => c.filter().sort())
        .visibility((v) => v.internal()),

      data: field(primitives.ref.longText)
        .optional()
        .nullable()
        .visibility((v) => v.internal()),
    },
    {
      extends: baseEntity,
      tags: ['notification'],
      description: 'Notification entity',
    },
  )
  .fieldSets({
    listSelect: (s) => s.only('id', 'title', 'channel', 'readAt'),
    listSort: (s) => s.only('createdAt', 'readAt'),
    listFilter: (s) => s.only('id', 'channel', 'user'),
  })
  .models({
    read: (m) => m.relations('expand'),
    create: (m) => m.omit('id', 'createdAt', 'updatedAt', 'deletedAt'),
    patch: (m) => m.partial().omit('id', 'createdAt', 'updatedAt', 'deletedAt'),
    public: (m) => m.pick('id', 'title', 'body', 'readAt'),
    internal: (m) => m.pick('id', 'title', 'body', 'channel', 'readAt'),
  });
