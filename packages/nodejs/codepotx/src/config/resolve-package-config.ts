import type { PackageConfig, OpenApiValidationConfig } from './package-config.types.js';
import { resolveOutputConfig } from '../output/resolve-output-config.js';
import { resolveCompileOptions } from './resolve-compile-options.js';

const defaultValidationConfig: OpenApiValidationConfig = {
  enabled: true,
  failOnWarnings: false,
  allowUnusedComponents: true,
};

const defaultLoggingConfig = {
  level: 'normal' as const,
};

export function resolvePackageConfig(config: PackageConfig) {
  return {
    contracts: config.contracts,
    output: resolveOutputConfig(config.output),
    compile: resolveCompileOptions(config),
    validation: {
      ...defaultValidationConfig,
      ...config.validation,
    },
    logging: {
      ...defaultLoggingConfig,
      ...config.logging,
    },
  };
}
