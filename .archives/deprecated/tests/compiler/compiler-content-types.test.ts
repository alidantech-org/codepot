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

describe('compiler route content types', () => {
  it('adds json content by default when route body has schema', () => {
    const ir = compile(v1.snapshot());
    const createUser = expectRouteMethod(ir.resources.users.routes, '/users', 'post');

    expect(createUser.body?.content_type).toEqual({
      $ref: '#/content_types/json',
    });

    expect(createUser.body?.content_types).toEqual([
      {
        $ref: '#/content_types/json',
      },
    ]);
  });

  it('preserves explicit body content types', () => {
    const ir = compile(v1.snapshot());
    const uploadAvatar = expectRouteMethod(ir.resources.users.routes, '/users/:id/avatar', 'post');

    expect(uploadAvatar.body?.content_type).toEqual({
      $ref: '#/content_types/multipart',
    });

    expect(uploadAvatar.body?.content_types).toEqual([
      {
        $ref: '#/content_types/multipart',
      },
    ]);
  });

  it('preserves multiple explicit output content types', () => {
    const ir = compile(v1.snapshot());
    const feedXml = expectRouteMethod(ir.resources.users.routes, '/users/feed.xml', 'get');

    expect(feedXml.responses[200]).toMatchObject({
      content_type: {
        $ref: '#/content_types/json',
      },
      content_types: [
        {
          $ref: '#/content_types/json',
        },
        {
          $ref: '#/content_types/xml',
        },
      ],
    });
  });

  it('does not add content types for no-content outputs', () => {
    const ir = compile(v1.snapshot());
    const deleteUser = expectRouteMethod(ir.resources.users.routes, '/users/:id', 'delete');

    expect(deleteUser.responses[204]).toEqual({
      status: 204,
    });
  });
});
