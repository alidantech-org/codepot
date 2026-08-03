import { field } from '@/index';

import { schemas } from '../version';
import { primitives, enums } from '../properties';
import { baseEntity } from './base.entity';

// ============================================================================
// WEBHOOK ENDPOINT ENTITY
// ============================================================================

export const webhookEndpoint = schemas
  .entity(
    'WebhookEndpoint',
    {
      tenant: field
        .relation()
        .required()
        .capability((c) => c.filter().select())
        .visibility((v) => v.internal()),

      deliveries: field
        .relation()
        .array()
        .visibility((v) => v.internal())
        .capability((c) => c.select()),

      name: field(primitives.ref.shortText)
        .required()
        .capability((c) => c.filter().sort())
        .visibility((v) => v.public()),

      url: field(primitives.ref.url)
        .required()
        .visibility((v) => v.secret()),

      secret: field(primitives.ref.apiKey)
        .required()
        .visibility((v) => v.secret()),

      eventTypes: field(enums.ref.WebhookEventType).array().required(),

      isActive: field(primitives.ref.boolean)
        .required()
        .capability((c) => c.filter())
        .visibility((v) => v.internal()),
    },
    {
      extends: baseEntity,
      tags: ['webhook'],
      description: 'Webhook endpoint entity',
    },
  )
  .fieldSets({
    listSelect: (s) => s.only('id', 'name', 'isActive'),
    listSort: (s) => s.only('createdAt', 'name'),
    listFilter: (s) => s.only('id', 'isActive', 'tenant'),
  })
  .models({
    read: (m) => m.relations('expand'),
    create: (m) => m.omit('id', 'createdAt', 'updatedAt', 'deletedAt', 'deliveries'),
    patch: (m) => m.partial().omit('id', 'createdAt', 'updatedAt', 'deletedAt', 'deliveries'),
    public: (m) => m.pick('id', 'name', 'isActive'),
    internal: (m) => m.pick('id', 'name', 'url', 'eventTypes', 'isActive'),
    redacted: (m) => m.omit('url', 'secret'),
  });