import { field } from '@/index';

import { schemas } from '../version';
import { primitives, enums, composites } from '../properties';
import { baseEntity } from './base.entity';

// ============================================================================
// PAYMENT ENTITY
// ============================================================================


export const payment = schemas
  .entity(
    'Payment',
    {
      invoice: field
        .relation()
        .required()
        .capability((c) => c.filter().select())
        .visibility((v) => v.internal()),

      amount: field(composites.ref.money).required(),

      status: field(enums.ref.PaymentStatus)
        .required()
        .capability((c) => c.filter().sort())
        .visibility((v) => v.public()),

      paymentMethod: field(primitives.ref.shortText)
        .required()
        .visibility((v) => v.internal()),

      transactionId: field(primitives.ref.externalId)
        .optional()
        .nullable()
        .visibility((v) => v.internal()),

      processedAt: field(primitives.ref.dateTime)
        .optional()
        .nullable()
        .capability((c) => c.filter().sort())
        .visibility((v) => v.public()),
    },
    {
      extends: baseEntity,
      tags: ['payment'],
      description: 'Payment entity',
    },
  )
  .fieldSets({
    listSelect: (s) => s.only('id', 'amount', 'status'),
    listSort: (s) => s.only('createdAt', 'status', 'processedAt'),
    listFilter: (s) => s.only('id', 'status', 'invoice'),
  })
  .models({
    read: (m) => m.relations('expand'),
    create: (m) => m.omit('id', 'createdAt', 'updatedAt', 'deletedAt'),
    patch: (m) => m.partial().omit('id', 'createdAt', 'updatedAt', 'deletedAt'),
    public: (m) => m.pick('id', 'amount', 'status', 'processedAt'),
    summary: (m) => m.pick('id', 'amount', 'status'),
  });
