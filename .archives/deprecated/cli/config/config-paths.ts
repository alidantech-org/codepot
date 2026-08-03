// cli/config/config-paths.ts

import { existsSync } from 'node:fs';
import { resolve } from 'node:path';

// ============================================================================
// CONSTANTS
// ============================================================================

export const DefaultConfigFileNames = ['codepot.config.ts', 'codepot.config.mts', 'codepot.config.js', 'codepot.config.mjs'] as const;

// ============================================================================
// PATHS
// ============================================================================

/**
 * Resolves a user-provided config path from cwd.
 */
export function resolveConfigPath(input: string, cwd = process.cwd()): string {
  return resolve(cwd, input);
}

/**
 * Finds the first default Codepot config file in cwd.
 */
export function findDefaultConfigPath(cwd = process.cwd()): string | undefined {
  for (const fileName of DefaultConfigFileNames) {
    const fullPath = resolve(cwd, fileName);

    if (existsSync(fullPath)) {
      return fullPath;
    }
  }

  return undefined;
}
