import { describe, expect, it } from 'vitest';

import { compile } from '@/compiler';
import type { HttpMethod, RouteMethodDefinition, RoutesDefinition } from '@/contract/types/ir/resource/route/definition';
import { v1 } from '../fixtures/contracts/v1-demo';

function expectRouteMethod(routes: RoutesDefinition, path: string, method: HttpMethod): RouteMethodDefinition {
  const pathRoute = routes[path];
  expect(pathRoute).toBeDefined();

  const routeMethod = pathRoute?.methods[method];
  expect(routeMethod).toBeDefined();

  return routeMethod as RouteMethodDefinition;
}

// ============================================================================
// TESTS
// ============================================================================

describe('compiler errors', () => {
  it('promotes resource-scoped errors to root responses with dotted keys', () => {
    const ir = compile(v1.snapshot());

    expect(ir.responses.errors['resource.users.email_taken']).toBeDefined();

    expect(ir.responses.errors['resource.users.email_taken']).toMatchObject({
      ownership: {
        $ref: '#/resources/users',
      },
      status: 409,
      schema: {
        $ref: '#/schemas/dtos/error_response',
      },
      content_type: {
        $ref: '#/content_types/json',
      },
    });

    expect(ir.responses.errors['users.email_taken']).toBeUndefined();
    expect(ir.responses.errors.users_email_taken).toBeUndefined();
  });

  it('keeps global errors at root without resource prefix', () => {
    const ir = compile(v1.snapshot());

    expect(ir.responses.errors.unauthorized).toBeDefined();
    expect(ir.responses.errors.forbidden).toBeDefined();
    expect(ir.responses.errors.not_found).toBeDefined();
    expect(ir.responses.errors.validation).toBeDefined();
  });

  it('uses compiled error statuses in route responses', () => {
    const ir = compile(v1.snapshot());
    const createUser = expectRouteMethod(ir.resources.users.routes, '/users', 'post');

    expect(createUser.responses[409]).toEqual({
      $ref: '#/responses/errors/resource.users.email_taken',
    });
  });

  it('does not place route errors under status 400', () => {
    const ir = compile(v1.snapshot());

    const listUsers = expectRouteMethod(ir.resources.users.routes, '/users', 'get');
    const createUser = expectRouteMethod(ir.resources.users.routes, '/users', 'post');

    expect(listUsers.responses[401]).toEqual({
      $ref: '#/responses/errors/unauthorized',
    });

    expect(listUsers.responses[403]).toEqual({
      $ref: '#/responses/errors/forbidden',
    });

    expect(createUser.responses[422]).toEqual({
      $ref: '#/responses/errors/validation',
    });

    expect(createUser.responses[409]).toEqual({
      $ref: '#/responses/errors/resource.users.email_taken',
    });

    expect(listUsers.responses[400]).toBeUndefined();
    expect(createUser.responses[400]).toBeUndefined();
  });
});
