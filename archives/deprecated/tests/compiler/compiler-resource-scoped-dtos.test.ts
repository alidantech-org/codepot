import { describe, expect, it } from 'vitest';

import { compile } from '@/compiler';
import { v1 } from '../fixtures/contracts/v1-demo';

// ============================================================================
// TESTS
// ============================================================================

describe('compiler resource-scoped DTOs', () => {
  it('keeps shared DTOs global', () => {
    const ir = compile(v1.snapshot());

    expect(ir.schemas.dtos.api_response).toBeDefined();
    expect(ir.schemas.dtos.paginated_response).toBeDefined();
    expect(ir.schemas.dtos.error_response).toBeDefined();

    expect(ir.schemas.dtos['resource.users.api_response']).toBeUndefined();
    expect(ir.schemas.dtos['resource.users.paginated_response']).toBeUndefined();
    expect(ir.schemas.dtos['resource.users.error_response']).toBeUndefined();
  });

  it('uses scoped DTO refs in user routes when DTOs are resource-local', () => {
    const ir = compile(v1.snapshot());
    const users = ir.resources.users;
    const routeJson = JSON.stringify(users.routes);

    if (ir.schemas.dtos['resource.users.user_response'] !== undefined) {
      expect(routeJson).toContain('#/schemas/dtos/resource.users.user_response');
      expect(ir.schemas.dtos['resource.users.user_response'].ownership).toEqual({
        $ref: '#/resources/users',
      });
    }

    if (ir.schemas.dtos['resource.users.user_list_response'] !== undefined) {
      expect(routeJson).toContain('#/schemas/dtos/resource.users.user_list_response');
      expect(ir.schemas.dtos['resource.users.user_list_response'].ownership).toEqual({
        $ref: '#/resources/users',
      });
    }

    if (ir.schemas.dtos['resource.users.create_user_body'] !== undefined) {
      expect(routeJson).toContain('#/schemas/dtos/resource.users.create_user_body');
      expect(ir.schemas.dtos['resource.users.create_user_body'].ownership).toEqual({
        $ref: '#/resources/users',
      });
    }
  });

  it('does not emit underscore-scoped user DTO keys', () => {
    const ir = compile(v1.snapshot());

    expect(ir.schemas.dtos['users.user_response']).toBeUndefined();
    expect(ir.schemas.dtos['users.user_list_response']).toBeUndefined();
    expect(ir.schemas.dtos['users.create_user_body']).toBeUndefined();

    expect(ir.schemas.dtos.users_user_response).toBeUndefined();
    expect(ir.schemas.dtos.users_user_list_response).toBeUndefined();
    expect(ir.schemas.dtos.users_create_user_body).toBeUndefined();
  });
});
