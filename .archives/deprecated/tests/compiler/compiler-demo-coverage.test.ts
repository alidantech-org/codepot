import { describe, expect, it } from 'vitest';

import { compile } from '@/compiler';
import { v1 } from '../fixtures/contracts/v1-demo';

describe('demo contract coverage', () => {
  it('compiles all expanded demo relations', () => {
    const ir = compile(v1.snapshot());

    expect(ir.schemas.entities.project.fields.tenant).toMatchObject({
      relation: 'belongs_to',
      target: {
        $ref: '#/schemas/entities/tenant',
      },
    });

    expect(ir.schemas.entities.project.fields.owner).toMatchObject({
      relation: 'belongs_to',
      target: {
        $ref: '#/schemas/entities/user',
      },
    });

    expect(ir.schemas.entities.project.fields.tasks).toMatchObject({
      relation: 'has_many',
      target: {
        $ref: '#/schemas/entities/task',
      },
    });

    expect(ir.schemas.entities.task.fields.project).toMatchObject({
      relation: 'belongs_to',
      target: {
        $ref: '#/schemas/entities/project',
      },
    });

    expect(ir.schemas.entities.task.fields.tags).toMatchObject({
      relation: 'many_to_many',
      target: {
        $ref: '#/schemas/entities/tag',
      },
      through: {
        entity: {
          $ref: '#/schemas/entities/task_tag',
        },
        from: {
          $ref: '#/schemas/entities/task_tag/fields/task',
        },
        to: {
          $ref: '#/schemas/entities/task_tag/fields/tag',
        },
      },
    });

    expect(ir.schemas.entities.task_comment.fields.task).toMatchObject({
      relation: 'belongs_to',
      target: {
        $ref: '#/schemas/entities/task',
      },
    });

    expect(ir.schemas.entities.invoice.fields.lines).toMatchObject({
      relation: 'has_many',
      target: {
        $ref: '#/schemas/entities/invoice_line',
      },
    });

    expect(ir.schemas.entities.payment.fields.invoice).toMatchObject({
      relation: 'belongs_to',
      target: {
        $ref: '#/schemas/entities/invoice',
      },
    });

    expect(ir.schemas.entities.audit_log.fields.user).toMatchObject({
      relation: 'belongs_to',
      target: {
        $ref: '#/schemas/entities/user',
      },
    });
  });
});
