/**
 * Config Loader Service
 *
 * Handles loading and validation of global codepot configuration.
 */

import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';

import type { codepotRuntime } from './codepot-runtime';
import type { ResolvedcodepotConfig } from '@/config/global/types/codepot.config.types';
import { importTsModule } from './ts-importer';

export interface ConfigLoaderOptions {
  configPath?: string;
}

export class ConfigLoader {
  constructor(private readonly runtime: codepotRuntime) {}

  /**
   * Loads the global codepot configuration.
   *
   * @param options - Configuration loading options
   * @returns Resolved global configuration
   */
  async loadGlobalConfig(options: ConfigLoaderOptions = {}): Promise<ResolvedcodepotConfig> {
    const configPath = options.configPath ?? this.runtime.configPath ?? 'codepot.config.ts';

    console.debug(`Config loader - loading config from: ${configPath}`);
    console.debug(`Config loader - cwd: ${this.runtime.cwd}`);

    try {
      const absoluteConfigPath = resolve(this.runtime.cwd, configPath);
      console.debug(`Config loader - absolute path: ${absoluteConfigPath}`);

      const configContent = await readFile(absoluteConfigPath, 'utf-8');
      console.debug(`Config loader - config file read successfully`);

      // Dynamic import of the config module using jiti TypeScript transpiler
      console.debug(`Config loader - Importing from: ${absoluteConfigPath}`);
      const configModule = await importTsModule(absoluteConfigPath);
      console.debug(`Config loader - module imported successfully`);

      const config = configModule.default ?? configModule;

      console.debug(`Config loader - loaded config:`, config);

      if (!config) {
        throw new Error(`No default export found in config file: ${configPath}`);
      }

      // Resolve configuration with defaults
      const resolvedConfig = this.resolveConfig(config);
      console.debug(`Config loader - resolved config:`, resolvedConfig);

      return resolvedConfig;
    } catch (error) {
      console.error(`Config loader - Error: ${error}`);
      console.error(`Config loader - Error details:`, error);
      if (error instanceof Error && error.message.includes('Cannot find module')) {
        throw new Error(`Configuration file not found: ${configPath}. Please run 'codepot init' first.`);
      }
      throw new Error(`Failed to load configuration: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * Resolves configuration with defaults and validation.
   *
   * @param config - Raw configuration object
   * @returns Resolved configuration
   */
  private resolveConfig(config: any): ResolvedcodepotConfig {
    const rootDir = config.rootDir || process.cwd();
    const manifestPath = config.manifestPath || './codepot/manifest.json';
    const outputDir = config.outputDir || './src/generated';
    const entitiesDir = config.entitiesDir || './code/configs/entities';
    const resourcesDir = config.resourcesDir || './code/configs/resources';

    return {
      rootDir,
      manifestPath,
      outputDir,
      entitiesDir,
      resourcesDir,
    };
  }
}
