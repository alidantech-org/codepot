import { describe, expect, it } from 'vitest';

import { compile } from '@/compiler';
import type { EntityFieldDefinition, EntityRelationFieldDefinition } from '@/contract/types/ir/schema/entity/field/definition';
import { v1 } from '../fixtures/contracts/v1-demo';

function expectRelationField(field: EntityFieldDefinition): EntityRelationFieldDefinition {
  expect(field).toHaveProperty('relation');

  return field as EntityRelationFieldDefinition;
}

// ============================================================================
// TESTS
// ============================================================================

describe('compiler relation refs', () => {
  it('compiles inverse relation refs using entity and field from authoring ref id', () => {
    const ir = compile(v1.snapshot());

    expect(expectRelationField(ir.schemas.entities.user.fields.profile).inverse).toEqual({
      $ref: '#/schemas/entities/profile/fields/user',
    });

    expect(expectRelationField(ir.schemas.entities.user.fields.posts).inverse).toEqual({
      $ref: '#/schemas/entities/post/fields/author',
    });

    expect(expectRelationField(ir.schemas.entities.post.fields.author).inverse).toEqual({
      $ref: '#/schemas/entities/user/fields/posts',
    });

    expect(expectRelationField(ir.schemas.entities.post.fields.tags).inverse).toEqual({
      $ref: '#/schemas/entities/tag/fields/posts',
    });
  });

  it('compiles many-to-many through refs using real entity field refs', () => {
    const ir = compile(v1.snapshot());

    expect(expectRelationField(ir.schemas.entities.post.fields.tags).through).toEqual({
      entity: {
        $ref: '#/schemas/entities/post_tag',
      },
      from: {
        $ref: '#/schemas/entities/post_tag/fields/post',
      },
      to: {
        $ref: '#/schemas/entities/post_tag/fields/tag',
      },
    });
  });
});
