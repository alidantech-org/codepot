// cli/commands/generate.ts

import { writeIrPackage } from '@/app';
import type { Logger } from '@/utils/logger';

import { loadCodepotConfig } from '../config/load-config';
import { createCliProgressReporter } from '../presentation/progress-reporter';

// ============================================================================
// TYPES
// ============================================================================

export interface GenerateCommandOptions {
  readonly cwd?: string;
  readonly config?: string;
  readonly logger: Logger;
}

// ============================================================================
// COMMAND
// ============================================================================

/**
 * Loads Codepot config, compiles contracts, and writes IR output.
 */
export async function runGenerateCommand(options: GenerateCommandOptions): Promise<void> {
  const loaded = await loadCodepotConfig({
    cwd: options.cwd,
    config: options.config,
  });

  options.logger.info(`Loaded config ${loaded.path}`);

  const result = await writeIrPackage(loaded.config, {
    progress: createCliProgressReporter(options.logger),
  });

  for (const file of result.files) {
    options.logger.success(`Generated ${file}`);
  }
}
