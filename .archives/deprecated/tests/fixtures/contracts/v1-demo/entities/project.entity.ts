import { field, property } from '@/index';

import { schemas } from '../version';
import { primitives, enums, composites } from '../properties';
import { baseEntity } from './base.entity';

// ============================================================================
// PROJECT ENTITY
// ============================================================================

export const project = schemas
  .entity(
    'Project',
    {
      tenant: field
        .relation()
        .required()
        .capability((c) => c.filter().select())
        .visibility((v) => v.internal()),

      owner: field
        .relation()
        .required()
        .capability((c) => c.filter().select())
        .visibility((v) => v.internal()),

      tasks: field
        .relation()
        .array()
        .visibility((v) => v.internal())
        .capability((c) => c.select()),

      name: field(primitives.ref.displayName)
        .required()
        .capability((c) => c.filter().sort().select())
        .visibility((v) => v.public()),

      slug: field(primitives.ref.slug)
        .required()
        .capability((c) => c.filter().sort())
        .visibility((v) => v.public()),

      status: field(enums.ref.ProjectStatus)
        .required()
        .capability((c) => c.filter().sort())
        .visibility((v) => v.public()),

      budget: field(composites.ref.money).optional(),

      inlineBudget: field(composites.ref.inlineMoney).optional(),

      // Inline enum on entity
      visibility: field(
        property.enum({
          private: { value: 'private', label: 'Private' },
          internal: { value: 'internal', label: 'Internal' },
          public: { value: 'public', label: 'Public' },
        }),
      )
        .required()
        .capability((c) => c.filter().sort())
        .visibility((v) => v.internal()),

      // Inline primitive on entity
      shortCode: field(property.string().minLength(3).maxLength(10))
        .optional()
        .visibility((v) => v.internal()),

      description: field(primitives.ref.description)
        .optional()
        .nullable()
        .visibility((v) => v.public()),
    },
    {
      extends: baseEntity,
      tags: ['project'],
      description: 'Project entity',
    },
  )
  .fieldSets({
    listSelect: (s) => s.only('id', 'name', 'slug', 'status'),
    listSort: (s) => s.only('createdAt', 'name', 'status'),
    listFilter: (s) => s.only('id', 'status', 'tenant', 'owner'),
    publicListSelect: (s) => s.only('id', 'name', 'slug'),
    adminListSelect: (s) => s.only('id', 'name', 'slug', 'status', 'visibility'),
  })
  .models({
    read: (m) => m.relations('expand'),
    create: (m) => m.omit('id', 'createdAt', 'updatedAt', 'deletedAt', 'tasks'),
    patch: (m) => m.partial().omit('id', 'createdAt', 'updatedAt', 'deletedAt', 'tasks'),
    public: (m) => m.pick('id', 'name', 'slug', 'status', 'description'),
    publicList: (m) => m.pick('id', 'name', 'slug'),
    admin: (m) => m.pick('id', 'name', 'slug', 'status', 'visibility', 'budget'),
    internal: (m) => m.pick('id', 'name', 'slug', 'status', 'visibility', 'shortCode'),
    summary: (m) => m.pick('id', 'name', 'status'),
    option: (m) => m.pick('id', 'name'),
    relation: (m) => m.pick('id', 'name', 'status'),
    projection: (m) => m.pick('id', 'name', 'slug', 'description'),
    redacted: (m) => m.omit('shortCode'),
  });