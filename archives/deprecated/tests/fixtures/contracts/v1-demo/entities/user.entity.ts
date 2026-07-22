import { field, property } from '@/index';

import { schemas } from '../version';
import { primitives, enums, composites } from '../properties';
import { baseEntity } from './base.entity';

// ============================================================================
// USER ENTITY
// ============================================================================


export const user = schemas
  .entity(
    'User',
    {
      tenant: field
        .relation()
        .required()
        .capability((c) => c.filter().select())
        .visibility((v) => v.internal()),

      profile: field
        .relation()
        .optional()
        .visibility((v) => v.internal()),

      posts: field
        .relation()
        .array()
        .visibility((v) => v.public())
        .capability((c) => c.select()),

      name: field(primitives.ref.displayName)
        .required()
        .capability((c) => c.filter().sort().select())
        .visibility((v) => v.public()),

      email: field(primitives.ref.email)
        .required()
        .capability((c) => c.filter().select(false))
        .visibility((v) => v.public().sensitive()),

      bio: field(primitives.ref.bio)
        .optional()
        .nullable()
        .visibility((v) => v.public()),

      nickname: field(property.string().minLength(2).maxLength(40))
        .optional()
        .visibility((v) => v.public()),

      role: field(enums.ref.UserRole)
        .required()
        .capability((c) => c.filter().sort())
        .visibility((v) => v.public()),

      roles: field(enums.ref.UserRole).array().required(),

      status: field(enums.ref.UserStatus)
        .required()
        .capability((c) => c.filter().sort())
        .visibility((v) => v.internal()),

      billingLimit: field(composites.ref.money).optional(),

      inlineBillingLimit: field(composites.ref.inlineMoney).optional(),
    },
    {
      extends: baseEntity,
      tags: ['auth', 'identity'],
      description: 'Application user',
    },
  )
  // .fieldSets({
  //   listSelect: (s) => s.only('id', 'name', 'role'),
  //   listSort: (s) => s.only('createdAt', 'role'),
  //   listFilter: (s) => s.only('id', 'role', 'status'),
  //   publicListSelect: (s) => s.only('id', 'name'),
  //   adminListSelect: (s) => s.only('id', 'name', 'email', 'role', 'status'),
  // })
  // .models({
  //   read: (m) => m.relations('expand'),
  //   create: (m) => m.partial().omit('id', 'createdAt', 'updatedAt', 'deletedAt', 'profile', 'posts'),
  //   patch: (m) => m.partial().omit('id', 'createdAt', 'updatedAt', 'deletedAt', 'profile', 'posts'),
  //   public: (m) => m.pick('id', 'name', 'bio', 'role'),
  // });
