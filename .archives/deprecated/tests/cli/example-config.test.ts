import { existsSync, readFileSync } from 'node:fs';

import { describe, expect, it } from 'vitest';

import { resolveExampleConfigPath } from '../../cli/config/example-config-path';

describe('example codepot config', () => {
  it('exists and contains a real starter contract', () => {
    const path = resolveExampleConfigPath();

    expect(existsSync(path)).toBe(true);

    const content = readFileSync(path, 'utf8');

    expect(content).toContain('defineCodepotConfig');
    expect(content).toContain('defineVersionContract');
    expect(content).toContain('defineProperties');
    expect(content).toContain('defineSchemas');
    expect(content).toContain('defineResource');
    expect(content).toContain('defineRoutes');
  });
});
