import { describe, expect, it } from 'vitest';

import { compile } from '@/compiler';
import { validateIrRefs } from '@/compiler/validators';
import { v1 } from '../fixtures/contracts/v1-demo';

describe('compiler IR ref validator', () => {
  it('emits no broken refs for the demo contract', () => {
    const ir = compile(v1.snapshot());

    expect(validateIrRefs(ir)).toEqual([]);
  });

  it('reports broken refs with path and ref', () => {
    const ir = compile(v1.snapshot()) as any;

    ir.schemas.dtos.bad_ref_test = {
      fields: {
        user: {
          $ref: '#/schemas/models/does_not_exist',
        },
      },
    };

    const issues = validateIrRefs(ir);

    expect(issues).toEqual([
      expect.objectContaining({
        ref: '#/schemas/models/does_not_exist',
      }),
    ]);
  });
});
