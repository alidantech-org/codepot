import { field } from '@/index';

import { schemas } from '../version';
import { primitives } from '../properties';
import { baseEntity } from './base.entity';

// ============================================================================
// TAG ENTITY
// ============================================================================

export const tag = schemas
  .entity(
    'Tag',
    {
      posts: field
        .relation()
        .array()
        .capability((c) => c.select()),

      tasks: field
        .relation()
        .array()
        .capability((c) => c.select()),

      name: field(primitives.ref.displayName)
        .required()
        .capability((c) => c.filter().sort()),
    },
    { extends: baseEntity },
  )
  .models({
    public: (m) => m.pick('id', 'name'),
    option: (m) => m.pick('id', 'name'),
  });
