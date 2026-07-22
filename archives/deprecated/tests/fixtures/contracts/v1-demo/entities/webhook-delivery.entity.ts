import { field } from '@/index';

import { schemas } from '../version';
import { primitives, enums } from '../properties';
import { baseEntity } from './base.entity';

// ============================================================================
// WEBHOOK DELIVERY ENTITY
// ============================================================================


export const webhookDelivery = schemas
  .entity(
    'WebhookDelivery',
    {
      endpoint: field
        .relation()
        .required()
        .capability((c) => c.filter().select())
        .visibility((v) => v.internal()),

      eventType: field(enums.ref.WebhookEventType)
        .required()
        .capability((c) => c.filter())
        .visibility((v) => v.internal()),

      payload: field(primitives.ref.longText)
        .required()
        .visibility((v) => v.internal()),

      responseStatus: field(primitives.ref.integer)
        .optional()
        .nullable()
        .visibility((v) => v.internal()),

      responseBody: field(primitives.ref.longText)
        .optional()
        .nullable()
        .visibility((v) => v.internal()),

      retryCount: field(primitives.ref.positiveInteger)
        .required()
        .default(0)
        .visibility((v) => v.internal()),

      deliveredAt: field(primitives.ref.dateTime)
        .optional()
        .nullable()
        .capability((c) => c.filter().sort())
        .visibility((v) => v.internal()),
    },
    {
      extends: baseEntity,
      tags: ['webhook_delivery'],
      description: 'Webhook delivery entity',
    },
  )
  .fieldSets({
    listSelect: (s) => s.only('id', 'eventType', 'responseStatus', 'retryCount'),
    listSort: (s) => s.only('createdAt', 'deliveredAt'),
    listFilter: (s) => s.only('id', 'eventType', 'endpoint'),
  })
  .models({
    read: (m) => m.relations('expand'),
    create: (m) => m.omit('id', 'createdAt', 'updatedAt', 'deletedAt'),
    patch: (m) => m.partial().omit('id', 'createdAt', 'updatedAt', 'deletedAt'),
    internal: (m) => m.pick('id', 'eventType', 'responseStatus', 'retryCount', 'deliveredAt'),
  });
