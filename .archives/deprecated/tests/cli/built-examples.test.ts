import { existsSync } from 'node:fs';
import { join } from 'node:path';

import { describe, expect, it } from 'vitest';

describe('built examples', () => {
  it('copies examples into dist during build when dist exists', () => {
    const distPath = join(process.cwd(), 'dist');

    if (!existsSync(distPath)) {
      return;
    }

    expect(existsSync(join(distPath, 'examples', 'codepot.config.ts'))).toBe(true);
  });
});
