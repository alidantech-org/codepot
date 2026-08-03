import { field } from '@/index';

import { schemas } from '../version';
import { primitives, enums } from '../properties';
import { baseEntity } from './base.entity';

// ============================================================================
// API KEY ENTITY
// ============================================================================


export const apiKey = schemas
  .entity(
    'ApiKey',
    {
      user: field
        .relation()
        .required()
        .capability((c) => c.filter().select())
        .visibility((v) => v.internal()),

      name: field(primitives.ref.shortText)
        .required()
        .capability((c) => c.filter().sort())
        .visibility((v) => v.public()),

      key: field(primitives.ref.apiKey)
        .required()
        .visibility((v) => v.secret()),

      status: field(enums.ref.ApiKeyStatus)
        .required()
        .capability((c) => c.filter().sort())
        .visibility((v) => v.internal()),

      lastUsedAt: field(primitives.ref.dateTime)
        .optional()
        .nullable()
        .capability((c) => c.filter().sort())
        .visibility((v) => v.internal()),

      expiresAt: field(primitives.ref.dateTime)
        .optional()
        .nullable()
        .capability((c) => c.filter())
        .visibility((v) => v.internal()),
    },
    {
      extends: baseEntity,
      tags: ['api_key'],
      description: 'API key entity',
    },
  )
  .fieldSets({
    listSelect: (s) => s.only('id', 'name', 'status'),
    listSort: (s) => s.only('createdAt', 'name', 'status'),
    listFilter: (s) => s.only('id', 'status', 'user'),
  })
  .models({
    read: (m) => m.relations('expand'),
    create: (m) => m.omit('id', 'createdAt', 'updatedAt', 'deletedAt'),
    patch: (m) => m.partial().omit('id', 'createdAt', 'updatedAt', 'deletedAt'),
    public: (m) => m.pick('id', 'name', 'status'),
    internal: (m) => m.pick('id', 'name', 'status', 'lastUsedAt', 'expiresAt'),
    redacted: (m) => m.omit('key'),
  });
