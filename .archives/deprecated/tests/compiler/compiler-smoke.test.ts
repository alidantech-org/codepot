import { describe, expect, it } from 'vitest';

import { compile } from '@/compiler';
import { v1 } from '../fixtures/contracts/v1-demo';

describe('compiler smoke test', () => {
  it('compiles demo authoring contract into Codepot IR', () => {
    const ir = compile(v1.snapshot());

    expect(ir.codepot).toBeDefined();
    expect(ir.key).toBeDefined();
    expect(ir.version).toBeDefined();

    expect(ir.content_types.json).toBeDefined();

    expect(Object.keys(ir.properties.primitives).length).toBeGreaterThan(0);
    expect(Object.keys(ir.schemas.entities).length).toBeGreaterThan(0);
    expect(Object.keys(ir.schemas.models).length).toBeGreaterThan(0);
    expect(Object.keys(ir.schemas.dtos).length).toBeGreaterThan(0);
    expect(Object.keys(ir.responses.errors).length).toBeGreaterThan(0);
    expect(Object.keys(ir.resources).length).toBeGreaterThan(0);
  });
});
