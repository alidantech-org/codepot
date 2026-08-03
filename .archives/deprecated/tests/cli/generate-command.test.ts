import { existsSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';

import { describe, expect, it } from 'vitest';

import { createLogger } from '@/utils/logger';
import { runGenerateCommand } from '../../cli/commands/generate';

describe('codepot generate', () => {
  it('loads config and writes IR files', async () => {
    const folder = mkdtempSync(join(tmpdir(), 'codepot-generate-'));

    try {
      const configPath = join(folder, 'codepot.config.mjs');
      const codepotUrl = pathToFileURL(join(process.cwd(), 'src', 'index.ts')).href;
      const outputFolder = join(folder, 'generated');

      writeFileSync(
        configPath,
        `
          import { defineCodepotConfig, defineVersionContract } from ${JSON.stringify(codepotUrl)};

          const v1 = defineVersionContract({
            key: 'cli_demo',
            version: 1,
            info: {
              title: 'CLI Demo',
              version: '1.0.0'
            }
          });

          export default defineCodepotConfig({
            contracts: [v1],
            output: {
              folder: ${JSON.stringify(outputFolder)}
            }
          });
        `,
        'utf8',
      );

      await runGenerateCommand({
        cwd: folder,
        config: configPath,
        logger: createLogger({ level: 'silent' }),
      });

      expect(existsSync(join(outputFolder, 'codepot.v1.json'))).toBe(true);
      expect(existsSync(join(outputFolder, 'codepot.v1.yaml'))).toBe(true);
    } finally {
      rmSync(folder, {
        recursive: true,
        force: true,
      });
    }
  });
});
