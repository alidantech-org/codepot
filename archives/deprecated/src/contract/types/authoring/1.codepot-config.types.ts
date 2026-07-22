import type { LoggerConfig } from '@/utils/logger';

import type { CompileOptions } from './0.compile-options.types';
import type { VersionBuilder } from './2.version-builder';

// ============================================================================
// URL ENVIRONMENT
// ============================================================================

export const UrlEnv = {
  local: 'local',
  development: 'development',
  preview: 'preview',
  staging: 'staging',
  production: 'production',
  test: 'test',
} as const;

export type UrlEnv = (typeof UrlEnv)[keyof typeof UrlEnv];

export const CodepotOutputFormat = {
  json: 'json',
  yaml: 'yaml',
} as const;

export type CodepotOutputFormat = (typeof CodepotOutputFormat)[keyof typeof CodepotOutputFormat];

export interface CodepotOutputConfig {
  readonly folder: string;
  readonly baseName: string;
  readonly formats: readonly CodepotOutputFormat[];
  readonly debugBaseName?: string;
}

export interface CodepotUrlConfig {
  readonly env: UrlEnv;
  readonly uri: string;
  readonly description?: string;
}

export interface CodepotValidationConfig {
  readonly enabled?: boolean;
  readonly failOnWarnings?: boolean;
  readonly allowUnusedDefinitions?: boolean;
}

export interface CodepotConfig {
  readonly contracts: readonly VersionBuilder[];

  readonly output?: Partial<CodepotOutputConfig>;

  readonly urls?: readonly CodepotUrlConfig[];

  readonly compile?: CompileOptions;

  readonly validation?: CodepotValidationConfig;

  readonly logging?: LoggerConfig;
}
