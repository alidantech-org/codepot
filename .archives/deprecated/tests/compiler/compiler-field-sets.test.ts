import { describe, expect, it } from 'vitest';

import { compile } from '@/compiler';
import { v1 } from '../fixtures/contracts/v1-demo';

// ============================================================================
// TESTS
// ============================================================================

describe('compiler field sets', () => {
  it('emits entity field-set overrides as owned root field_sets with dotted keys', () => {
    const ir = compile(v1.snapshot());

    expect(ir.schemas.field_sets['entity.user.list_select']).toEqual({
      ownership: {
        $ref: '#/schemas/entities/user',
      },
      fields: [
        {
          $ref: '#/schemas/entities/base_entity/fields/id',
        },
        {
          $ref: '#/schemas/entities/user/fields/name',
        },
        {
          $ref: '#/schemas/entities/user/fields/role',
        },
      ],
    });

    expect(ir.schemas.field_sets['entity.user.list_sort']).toMatchObject({
      ownership: {
        $ref: '#/schemas/entities/user',
      },
      fields: [
        {
          $ref: '#/schemas/entities/base_entity/fields/created_at',
        },
        {
          $ref: '#/schemas/entities/user/fields/role',
        },
      ],
    });

    expect(ir.schemas.field_sets['entity.user.list_filter']).toMatchObject({
      ownership: {
        $ref: '#/schemas/entities/user',
      },
      fields: [
        {
          $ref: '#/schemas/entities/base_entity/fields/id',
        },
        {
          $ref: '#/schemas/entities/user/fields/role',
        },
        {
          $ref: '#/schemas/entities/user/fields/status',
        },
      ],
    });
  });

  it('emits public and admin field sets with inherited refs when requested', () => {
    const ir = compile(v1.snapshot());

    expect(ir.schemas.field_sets['entity.user.public_list_select']?.fields).toEqual([
      {
        $ref: '#/schemas/entities/base_entity/fields/id',
      },
      {
        $ref: '#/schemas/entities/user/fields/name',
      },
    ]);

    expect(ir.schemas.field_sets['entity.user.admin_list_select']?.fields).toEqual([
      {
        $ref: '#/schemas/entities/base_entity/fields/id',
      },
      {
        $ref: '#/schemas/entities/user/fields/name',
      },
      {
        $ref: '#/schemas/entities/user/fields/email',
      },
      {
        $ref: '#/schemas/entities/user/fields/role',
      },
      {
        $ref: '#/schemas/entities/user/fields/status',
      },
    ]);
  });

  it('generates default metadata-based field sets for every entity', () => {
    const ir = compile(v1.snapshot());

    expect(ir.schemas.field_sets['entity.user.all_fields']).toBeDefined();
    expect(ir.schemas.field_sets['entity.user.owned_fields']).toBeDefined();
    expect(ir.schemas.field_sets['entity.user.inherited_fields']).toBeDefined();
    expect(ir.schemas.field_sets['entity.user.stored_fields']).toBeDefined();
    expect(ir.schemas.field_sets['entity.user.relation_fields']).toBeDefined();
    expect(ir.schemas.field_sets['entity.user.filter_fields']).toBeDefined();
    expect(ir.schemas.field_sets['entity.user.sort_fields']).toBeDefined();
    expect(ir.schemas.field_sets['entity.user.select_fields']).toBeDefined();
    expect(ir.schemas.field_sets['entity.user.public_fields']).toBeDefined();
    expect(ir.schemas.field_sets['entity.user.create_fields']).toBeDefined();
    expect(ir.schemas.field_sets['entity.user.update_fields']).toBeDefined();
  });

  it('generated field sets use ownership and field refs', () => {
    const ir = compile(v1.snapshot());

    expect(ir.schemas.field_sets['entity.user.filter_fields']).toMatchObject({
      ownership: {
        $ref: '#/schemas/entities/user',
      },
    });

    expect(ir.schemas.field_sets['entity.user.filter_fields'].fields).toEqual(
      expect.arrayContaining([
        { $ref: '#/schemas/entities/base_entity/fields/id' },
        { $ref: '#/schemas/entities/user/fields/role' },
        { $ref: '#/schemas/entities/user/fields/status' },
      ]),
    );
  });

  it('generated relation field sets include relation fields', () => {
    const ir = compile(v1.snapshot());

    expect(ir.schemas.field_sets['entity.user.relation_fields'].fields).toEqual(
      expect.arrayContaining([
        { $ref: '#/schemas/entities/user/fields/tenant' },
        { $ref: '#/schemas/entities/user/fields/profile' },
        { $ref: '#/schemas/entities/user/fields/posts' },
      ]),
    );
  });

  it('emits field sets as owned objects containing field refs', () => {
    const ir = compile(v1.snapshot());

    for (const [key, fieldSet] of Object.entries(ir.schemas.field_sets)) {
      expect(key.split('.')).toHaveLength(3);
      expect(key.startsWith('entity.')).toBe(true);

      expect(fieldSet).toHaveProperty('ownership');
      expect(fieldSet.ownership).toHaveProperty('$ref');
      expect(Array.isArray(fieldSet.fields)).toBe(true);

      for (const fieldRef of fieldSet.fields) {
        expect(fieldRef).toHaveProperty('$ref');
        expect(Object.keys(fieldRef)).toEqual(['$ref']);
      }
    }
  });

  it('does not duplicate inherited fields inside child entity fields', () => {
    const ir = compile(v1.snapshot());

    expect(ir.schemas.entities.user.fields.id).toBeUndefined();
    expect(ir.schemas.entities.user.fields.created_at).toBeUndefined();

    expect(ir.schemas.entities.base_entity.fields.id).toBeDefined();
    expect(ir.schemas.entities.base_entity.fields.created_at).toBeDefined();
  });

  it('throws when a field-set references an unknown field', () => {
    const snapshot = v1.snapshot() as any;

    snapshot.schemas.entities.User.fieldSetOverrides.badSet = {
      mode: 'only',
      fields: ['doesNotExist'],
    };

    expect(() => compile(snapshot)).toThrow('Field set references unknown field "user.does_not_exist".');
  });
});
