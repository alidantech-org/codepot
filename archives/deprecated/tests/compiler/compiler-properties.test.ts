import { describe, expect, it } from 'vitest';

import { compile } from '@/compiler';
import { v1 } from '../fixtures/contracts/v1-demo';

describe('compiler properties', () => {
  it('normalizes primitive format values into IR format values', () => {
    const ir = compile(v1.snapshot());

    expect(ir.properties.primitives.date_time.format).toBe('date-time');
  });

  it('normalizes primitive validation keys into snake_case', () => {
    const ir = compile(v1.snapshot());

    expect(ir.properties.primitives.display_name.validation).toEqual({
      min_length: 2,
      max_length: 80,
    });
  });
});
