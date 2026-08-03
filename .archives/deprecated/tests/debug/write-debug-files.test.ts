import { existsSync, readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';

import { writeAuthoringDebugPackage } from '@/app';
import { demoConfig } from '../fixtures/contracts/v1-demo';

describe('writeDebugFiles', () => {
  it('writes authoring debug json and yaml files', async () => {
    const result = await writeAuthoringDebugPackage(demoConfig);

    expect(result.files).toEqual(['tests/generated/debug/demo.authoring.json', 'tests/generated/debug/demo.authoring.yaml']);

    for (const file of result.files) {
      expect(existsSync(file)).toBe(true);
    }

    const json = readFileSync('tests/generated/debug/demo.authoring.json', 'utf8');

    const yaml = readFileSync('tests/generated/debug/demo.authoring.yaml', 'utf8');

    expect(json).toContain('security:credential:bearer');
    expect(json).toContain('security:policy:tenantAdmin');
    expect(json).not.toContain('"$ref"');
    expect(json).not.toContain('#/schemas');

    expect(yaml).toContain('security:credential:bearer');
    expect(yaml).toContain('security:policy:tenantAdmin');
    expect(yaml).not.toContain('$ref');
    expect(yaml).not.toContain('#/schemas');
  });
});
