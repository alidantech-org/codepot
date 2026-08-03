import { describe, expect, it } from 'vitest';

import { compile } from '@/compiler';
import { v1 } from '../fixtures/contracts/v1-demo';

// ============================================================================
// TESTS
// ============================================================================

describe('compiler DTOs', () => {
  it('compiles extendWith DTO composition into fields', () => {
    const ir = compile(v1.snapshot());

    expect(ir.schemas.dtos.user_response.extends).toEqual({
      $ref: '#/schemas/dtos/api_response',
    });

    expect(ir.schemas.dtos.user_response.fields.user).toEqual({
      $ref: '#/schemas/models/entity.user.user_public',
      required: true,
    });

    expect(ir.schemas.dtos.user_list_response.extends).toEqual({
      $ref: '#/schemas/dtos/paginated_response',
    });

    expect(ir.schemas.dtos.user_list_response.fields.items).toEqual({
      $ref: '#/schemas/models/entity.user.user_public',
      array: true,
      required: true,
    });
  });

  it('preserves DTO field usage metadata', () => {
    const ir = compile(v1.snapshot());

    expect(ir.schemas.dtos.error_response.fields.message).toEqual({
      $ref: '#/properties/primitives/message',
      required: true,
    });

    expect(ir.schemas.dtos.error_response.fields.code).toEqual({
      $ref: '#/properties/primitives/text',
      required: false,
    });
  });
});
