import { field } from '@/index';

import { schemas } from '../version';
import { primitives, enums, composites } from '../properties';
import { baseEntity } from './base.entity';

// ============================================================================
// INVOICE ENTITY
// ============================================================================

export const invoice = schemas
  .entity(
    'Invoice',
    {
      tenant: field
        .relation()
        .required()
        .capability((c) => c.filter().select())
        .visibility((v) => v.internal()),

      lines: field
        .relation()
        .array()
        .visibility((v) => v.internal())
        .capability((c) => c.select()),

      payments: field
        .relation()
        .array()
        .visibility((v) => v.internal())
        .capability((c) => c.select()),

      invoiceNumber: field(primitives.ref.shortText)
        .required()
        .capability((c) => c.filter().sort())
        .visibility((v) => v.public()),

      status: field(enums.ref.InvoiceStatus)
        .required()
        .capability((c) => c.filter().sort())
        .visibility((v) => v.public()),

      subtotal: field(composites.ref.money).required(),

      tax: field(composites.ref.money).required(),

      total: field(composites.ref.money).required(),

      dueAt: field(primitives.ref.dateTime)
        .required()
        .capability((c) => c.filter().sort())
        .visibility((v) => v.public()),

      paidAt: field(primitives.ref.dateTime)
        .optional()
        .nullable()
        .capability((c) => c.filter().sort())
        .visibility((v) => v.public()),
    },
    {
      extends: baseEntity,
      tags: ['invoice'],
      description: 'Invoice entity',
    },
  )
  .fieldSets({
    listSelect: (s) => s.only('id', 'invoiceNumber', 'status', 'total'),
    listSort: (s) => s.only('createdAt', 'invoiceNumber', 'status', 'dueAt'),
    listFilter: (s) => s.only('id', 'status', 'tenant'),
    publicListSelect: (s) => s.only('id', 'invoiceNumber', 'status'),
    adminListSelect: (s) => s.only('id', 'invoiceNumber', 'status', 'total', 'dueAt'),
  })
  .models({
    read: (m) => m.relations('expand'),
    create: (m) => m.omit('id', 'createdAt', 'updatedAt', 'deletedAt', 'lines', 'payments'),
    patch: (m) => m.partial().omit('id', 'createdAt', 'updatedAt', 'deletedAt', 'lines', 'payments'),
    public: (m) => m.pick('id', 'invoiceNumber', 'status', 'total', 'dueAt'),
    publicList: (m) => m.pick('id', 'invoiceNumber', 'status'),
    admin: (m) => m.pick('id', 'invoiceNumber', 'status', 'subtotal', 'tax', 'total', 'dueAt', 'paidAt'),
    summary: (m) => m.pick('id', 'invoiceNumber', 'status', 'total'),
  });