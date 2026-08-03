import { describe, expect, it } from 'vitest';

import { compile } from '@/compiler';
import { v1 } from '../fixtures/contracts/v1-demo';

// ============================================================================
// TESTS
// ============================================================================

describe('compiler schema refs', () => {
  it('resolves model refs with entity and variant into model keys', () => {
    const ir = compile(v1.snapshot());

    expect(ir.schemas.dtos.user_public.extends).toEqual({
      $ref: '#/schemas/models/entity.user.user_public',
    });

    expect(ir.schemas.dtos.user_patch_body.extends).toEqual({
      $ref: '#/schemas/models/entity.user.user_patch',
    });

    expect(ir.schemas.dtos.post_public.extends).toEqual({
      $ref: '#/schemas/models/entity.post.post_public',
    });
  });

  it('resolves DTO query entity field refs using entity from authoring ref id', () => {
    const ir = compile(v1.snapshot());

    expect(ir.schemas.dtos.list_users_query.fields.role).toMatchObject({
      $ref: '#/schemas/entities/user/fields/role',
    });

    expect(ir.schemas.dtos.list_users_query.fields.status).toMatchObject({
      $ref: '#/schemas/entities/user/fields/status',
    });

    expect(ir.schemas.dtos.list_posts_query.fields.author).toMatchObject({
      $ref: '#/schemas/entities/post/fields/author',
    });
  });
});
