import { field } from '@/index';

import { schemas } from '../version';
import { primitives, enums } from '../properties';
import { baseEntity } from './base.entity';

// ============================================================================
// POST ENTITY
// ============================================================================

export const post = schemas
  .entity(
    'Post',
    {
      author: field
        .relation()
        .required()
        .capability((c) => c.filter().select())
        .visibility((v) => v.internal()),

      tags: field
        .relation()
        .array()
        .visibility((v) => v.public())
        .capability((c) => c.select()),

      relatedProfiles: field
        .relation()
        .array()
        .visibility((v) => v.internal())
        .capability((c) => c.select()),

      title: field(primitives.ref.title)
        .required()
        .capability((c) => c.filter().sort().select())
        .visibility((v) => v.public()),

      body: field(primitives.ref.bio)
        .required()
        .visibility((v) => v.public()),

      status: field(enums.ref.PostStatus)
        .required()
        .capability((c) => c.filter().sort())
        .visibility((v) => v.public()),
    },
    { extends: baseEntity },
  )
  .models({
    read: (m) => m.relations('expand'),
    public: (m) => m.pick('id', 'author', 'title', 'body', 'status', 'tags'),
    create: (m) => m.omit('id', 'createdAt', 'updatedAt', 'deletedAt', 'author', 'tags', 'relatedProfiles'),
    patch: (m) => m.partial().omit('id', 'createdAt', 'updatedAt', 'deletedAt', 'author', 'tags', 'relatedProfiles'),
  });