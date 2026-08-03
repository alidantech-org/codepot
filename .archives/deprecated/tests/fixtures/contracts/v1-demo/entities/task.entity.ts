import { field } from '@/index';

import { schemas } from '../version';
import { primitives, enums } from '../properties';
import { baseEntity } from './base.entity';

// ============================================================================
// TASK ENTITY
// ============================================================================

export const task = schemas
  .entity(
    'Task',
    {
      project: field
        .relation()
        .required()
        .capability((c) => c.filter().select())
        .visibility((v) => v.internal()),

      assignee: field
        .relation()
        .optional()
        .capability((c) => c.filter().select())
        .visibility((v) => v.internal()),

      comments: field
        .relation()
        .array()
        .visibility((v) => v.internal())
        .capability((c) => c.select()),

      attachments: field
        .relation()
        .array()
        .visibility((v) => v.internal())
        .capability((c) => c.select()),

      tags: field
        .relation()
        .array()
        .visibility((v) => v.public())
        .capability((c) => c.select()),

      title: field(primitives.ref.title)
        .required()
        .capability((c) => c.filter().sort().select())
        .visibility((v) => v.public()),

      description: field(primitives.ref.longText)
        .optional()
        .nullable()
        .visibility((v) => v.public()),

      status: field(enums.ref.TaskStatus)
        .required()
        .capability((c) => c.filter().sort())
        .visibility((v) => v.public()),

      priority: field(enums.ref.TaskPriority)
        .required()
        .capability((c) => c.filter().sort())
        .visibility((v) => v.public()),

      dueAt: field(primitives.ref.dateTime)
        .optional()
        .nullable()
        .capability((c) => c.filter().sort())
        .visibility((v) => v.public()),

      estimateSeconds: field(primitives.ref.durationSeconds)
        .optional()
        .nullable()
        .visibility((v) => v.internal()),
    },
    {
      extends: baseEntity,
      tags: ['task'],
      description: 'Task entity',
    },
  )
  .fieldSets({
    listSelect: (s) => s.only('id', 'title', 'status', 'priority'),
    listSort: (s) => s.only('createdAt', 'title', 'status', 'priority', 'dueAt'),
    listFilter: (s) => s.only('id', 'status', 'priority', 'project', 'assignee', 'dueAt'),
    publicListSelect: (s) => s.only('id', 'title', 'status'),
    adminListSelect: (s) => s.only('id', 'title', 'status', 'priority', 'assignee'),
  })
  .models({
    read: (m) => m.relations('expand'),
    create: (m) => m.omit('id', 'createdAt', 'updatedAt', 'deletedAt', 'comments', 'attachments', 'tags'),
    patch: (m) => m.partial().omit('id', 'createdAt', 'updatedAt', 'deletedAt', 'comments', 'attachments', 'tags'),
    public: (m) => m.pick('id', 'title', 'description', 'status', 'priority', 'dueAt'),
    publicList: (m) => m.pick('id', 'title', 'status'),
    admin: (m) => m.pick('id', 'title', 'status', 'priority', 'assignee', 'dueAt'),
    internal: (m) => m.pick('id', 'title', 'status', 'priority', 'estimateSeconds'),
    summary: (m) => m.pick('id', 'title', 'status'),
    option: (m) => m.pick('id', 'title'),
    relation: (m) => m.pick('id', 'title', 'status'),
    projection: (m) => m.pick('id', 'title', 'description'),
    redacted: (m) => m.omit('estimateSeconds'),
  });