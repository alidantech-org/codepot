// cli/commands/init.ts

import { existsSync } from 'node:fs';
import { copyFile } from 'node:fs/promises';
import { resolve } from 'node:path';

import type { Logger } from '@/utils/logger';

import { resolveExampleConfigPath } from '../config/example-config-path';

// ============================================================================
// TYPES
// ============================================================================

export interface InitCommandOptions {
  readonly cwd?: string;
  readonly force?: boolean;
  readonly logger: Logger;
}

// ============================================================================
// COMMAND
// ============================================================================

/**
 * Creates a starter codepot.config.ts file by copying the package example.
 */
export async function runInitCommand(options: InitCommandOptions): Promise<void> {
  const cwd = options.cwd ?? process.cwd();
  const targetPath = resolve(cwd, 'codepot.config.ts');
  const sourcePath = resolveExampleConfigPath();

  if (!existsSync(sourcePath)) {
    throw new Error(`Starter config example was not found at "${sourcePath}".`);
  }

  if (existsSync(targetPath) && !options.force) {
    throw new Error('codepot.config.ts already exists. Pass --force to overwrite it.');
  }

  await copyFile(sourcePath, targetPath);

  options.logger.success('Created codepot.config.ts');
}
