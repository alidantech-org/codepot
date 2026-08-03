// cli/config/load-config.ts

import { resolve } from 'node:path';

import { createJiti } from 'jiti';

import type { CodepotConfig } from '@/contract/types/authoring/1.codepot-config.types';

import { findDefaultConfigPath, resolveConfigPath } from './config-paths';

// ============================================================================
// TYPES
// ============================================================================

export interface LoadCodepotConfigOptions {
  readonly config?: string;
  readonly cwd?: string;
}

export interface LoadedCodepotConfig {
  readonly path: string;
  readonly config: CodepotConfig;
}

// ============================================================================
// LOAD
// ============================================================================

/**
 * Loads a Codepot config module.
 */
export async function loadCodepotConfig(options: LoadCodepotConfigOptions = {}): Promise<LoadedCodepotConfig> {
  const cwd = options.cwd ?? process.cwd();
  const configPath = options.config !== undefined ? resolveConfigPath(options.config, cwd) : findDefaultConfigPath(cwd);

  if (configPath === undefined) {
    throw new Error('No Codepot config found. Run `codepot init` or pass --config <path>.');
  }

  const jiti = createJiti(import.meta.url, {
    tsconfigPaths: resolve(process.cwd(), 'tsconfig.json'),
  });
  const module = await jiti.import<Record<string, unknown>>(configPath);
  const config = module.default ?? module.config;

  if (config === undefined) {
    throw new Error(`Config file "${configPath}" must export default config.`);
  }

  return {
    path: configPath,
    config: config as CodepotConfig,
  };
}
