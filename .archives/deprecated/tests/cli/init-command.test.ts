import { existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

import { describe, expect, it } from 'vitest';

import { createLogger } from '@/utils/logger';
import { runInitCommand } from '../../cli/commands/init';

describe('codepot init', () => {
  it('creates codepot.config.ts', async () => {
    const folder = mkdtempSync(join(tmpdir(), 'codepot-init-'));

    try {
      await runInitCommand({
        cwd: folder,
        logger: createLogger({ level: 'silent' }),
      });

      const configPath = join(folder, 'codepot.config.ts');
      const content = readFileSync(configPath, 'utf8');

      expect(existsSync(configPath)).toBe(true);
      expect(content).toContain('defineCodepotConfig');
      expect(content).toContain('defineVersionContract');
      expect(content).toContain('defineResource');
      expect(content).toContain('contracts: [v1]');
    } finally {
      rmSync(folder, {
        recursive: true,
        force: true,
      });
    }
  });

  it('does not overwrite existing config unless force is passed', async () => {
    const folder = mkdtempSync(join(tmpdir(), 'codepot-init-'));

    try {
      const configPath = join(folder, 'codepot.config.ts');

      writeFileSync(configPath, 'existing config', 'utf8');

      await expect(
        runInitCommand({
          cwd: folder,
          logger: createLogger({ level: 'silent' }),
        }),
      ).rejects.toThrow('already exists');

      expect(readFileSync(configPath, 'utf8')).toBe('existing config');

      await runInitCommand({
        cwd: folder,
        force: true,
        logger: createLogger({ level: 'silent' }),
      });

      expect(readFileSync(configPath, 'utf8')).toContain('defineCodepotConfig');
    } finally {
      rmSync(folder, {
        recursive: true,
        force: true,
      });
    }
  });
});
