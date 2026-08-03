import { describe, expect, it } from 'vitest';

import { compile } from '@/compiler';
import { v1 } from '../fixtures/contracts/v1-demo';

describe('compiler model field sets', () => {
  it('links query models to generated capability field sets', () => {
    const ir = compile(v1.snapshot());

    expect(ir.schemas.models['entity.user.user_query'].field_sets).toMatchObject({
      select: {
        $ref: '#/schemas/field_sets/entity.user.select_fields',
      },
      sort: {
        $ref: '#/schemas/field_sets/entity.user.sort_fields',
      },
      filter: {
        $ref: '#/schemas/field_sets/entity.user.filter_fields',
      },
    });
  });

  it('links public models to generated public field sets', () => {
    const ir = compile(v1.snapshot());

    expect(ir.schemas.models['entity.user.user_public'].field_sets?.select).toEqual({
      $ref: '#/schemas/field_sets/entity.user.public_fields',
    });

    expect(ir.schemas.models['entity.user.user_public_list'].field_sets?.select).toEqual({
      $ref: '#/schemas/field_sets/entity.user.public_fields',
    });
  });

  it('links create and patch models to lifecycle field sets', () => {
    const ir = compile(v1.snapshot());

    expect(ir.schemas.models['entity.user.user_create'].field_sets?.create).toEqual({
      $ref: '#/schemas/field_sets/entity.user.create_fields',
    });

    expect(ir.schemas.models['entity.user.user_patch'].field_sets?.update).toEqual({
      $ref: '#/schemas/field_sets/entity.user.update_fields',
    });
  });

  it('links models to generated relation field sets', () => {
    const ir = compile(v1.snapshot());

    expect(ir.schemas.models['entity.user.user_read'].field_sets?.relations).toEqual({
      $ref: '#/schemas/field_sets/entity.user.relation_fields',
    });
  });
});
