// cli/config/example-config-path.ts

import { existsSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

// ============================================================================
// CONSTANTS
// ============================================================================

export const ExampleConfigFileName = 'codepot.config.ts';

// ============================================================================
// PATHS
// ============================================================================

/**
 * Resolves the package-local examples directory.
 *
 * Supported layouts:
 * - cli/config/example-config-path.ts -> package root /examples
 * - dist/cli/config/example-config-path.js -> dist/examples
 * - dist/cli/index.js bundled by tsup -> dist/examples
 */
export function resolveExamplesDirectory(): string {
  const currentFile = fileURLToPath(import.meta.url);
  const currentDir = dirname(currentFile);

  const candidateDirectories = [resolve(currentDir, '..', 'examples'), resolve(currentDir, '..', '..', 'examples')];

  for (const directory of candidateDirectories) {
    if (existsSync(join(directory, ExampleConfigFileName))) {
      return directory;
    }
  }

  return candidateDirectories[candidateDirectories.length - 1];
}

/**
 * Resolves the source example config file copied by `codepot init`.
 */
export function resolveExampleConfigPath(): string {
  return join(resolveExamplesDirectory(), ExampleConfigFileName);
}
