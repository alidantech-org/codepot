import type { PackageConfig } from '../config/package-config.types.js';
import type { Logger } from '../logging/logger.types.js';
import type { GenerateOpenApiResult } from '../generator/generate-openapi.js';

export interface InitConfigInput {
  readonly cwd?: string;
  readonly fileName?: string;
  readonly force?: boolean;
}

export interface InitConfigResult {
  readonly success: boolean;
  readonly filePath?: string;
  readonly skipped?: boolean;
  readonly error?: unknown;
}

export interface GenerateInput {
  readonly config: PackageConfig;
  readonly logger?: Logger;
}

export type GenerateResult = GenerateOpenApiResult;

export interface OpenApiTsApi {
  initConfig(input?: InitConfigInput): Promise<InitConfigResult>;
  generate(input: GenerateInput): Promise<GenerateResult>;
}
