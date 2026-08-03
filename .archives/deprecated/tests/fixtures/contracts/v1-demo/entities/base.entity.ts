import { field } from '@/index';

import { schemas } from '../version';
import { primitives } from '../properties';


// ============================================================================
// BASE ENTITY
// ============================================================================

export const baseEntity = schemas.entity(
  'BaseEntity',
  {
    id: field(primitives.ref.id)
      .required()
      .capability((c) => c.filter().sort().select())
      .lifecycle((l) => l.generated().immutable())
      .persistence((p) => p.stored()),

    createdAt: field(primitives.ref.dateTime)
      .required()
      .capability((c) => c.filter().sort())
      .lifecycle((l) => l.immutable())
      .persistence((p) => p.stored()),

    updatedAt: field(primitives.ref.dateTime)
      .required()
      .persistence((p) => p.stored()),

    deletedAt: field(primitives.ref.dateTime)
      .optional()
      .nullable()
      .capability((c) => c.filter())
      .lifecycle((l) => l.immutable())
      .persistence((p) => p.stored()),
  },
  { abstract: true },
);