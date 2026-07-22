import { field } from '@/index';

import { schemas } from '../version';
import { primitives, composites } from '../properties';
import { baseEntity } from './base.entity';

// ============================================================================
// INVOICE LINE ENTITY
// ============================================================================


export const invoiceLine = schemas
  .entity(
    'InvoiceLine',
    {
      invoice: field
        .relation()
        .required()
        .capability((c) => c.filter())
        .visibility((v) => v.internal()),

      description: field(primitives.ref.description)
        .required()
        .visibility((v) => v.public()),

      quantity: field(primitives.ref.positiveInteger)
        .required()
        .visibility((v) => v.public()),

      unitPrice: field(composites.ref.money).required(),

      lineTotal: field(composites.ref.money).required(),
    },
    {
      extends: baseEntity,
      tags: ['invoice_line'],
      description: 'Invoice line entity',
    },
  )
  .models({
    read: (m) => m.relations('expand'),
    create: (m) => m.omit('id', 'createdAt', 'updatedAt', 'deletedAt'),
    patch: (m) => m.partial().omit('id', 'createdAt', 'updatedAt', 'deletedAt'),
    public: (m) => m.pick('id', 'description', 'quantity', 'unitPrice', 'lineTotal'),
  });
