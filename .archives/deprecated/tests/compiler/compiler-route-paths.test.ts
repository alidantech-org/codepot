import { describe, expect, it } from 'vitest';

import { compile } from '@/compiler';
import { v1 } from '../fixtures/contracts/v1-demo';

describe('compiler route paths', () => {
  it('emits full route paths including resource base path', () => {
    const ir = compile(v1.snapshot());

    expect(ir.resources.users.routes['/users']).toBeDefined();
    expect(ir.resources.users.routes['/users/:id']).toBeDefined();
    expect(ir.resources.posts.routes['/posts']).toBeDefined();
    expect(ir.resources.posts.routes['/posts/:id']).toBeDefined();

    expect(ir.resources.users.routes['/']).toBeUndefined();
    expect(ir.resources.users.routes['/:id']).toBeUndefined();
  });

  it('emits HTTP methods under route path methods', () => {
    const ir = compile(v1.snapshot());

    expect(ir.resources.users.routes['/users'].methods.get).toBeDefined();
    expect(ir.resources.users.routes['/users'].methods.post).toBeDefined();
    expect(ir.resources.users.routes['/users/:id'].methods.get).toBeDefined();
    expect(ir.resources.users.routes['/users/:id'].methods.delete).toBeDefined();
  });

  it('emits path-level parameters for parameterized paths', () => {
    const ir = compile(v1.snapshot());

    expect(ir.resources.users.routes['/users/:id'].parameters).toEqual({
      id: {
        $ref: '#/schemas/params/resource.users.id',
      },
    });

    expect(ir.resources.posts.routes['/posts/:id'].parameters).toEqual({
      id: {
        $ref: '#/schemas/params/resource.posts.id',
      },
    });
  });
});
