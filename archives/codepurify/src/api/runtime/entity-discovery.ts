/**
 * Entity Discovery Service
 *
 * Handles discovery of entity configuration files in the project.
 */

import fastGlob from 'fast-glob';
import { resolve, relative } from 'node:path';

import type { CodepurifyRuntime } from './codepurify-runtime';
import type { ResolvedCodepurifyConfig } from '@/config/global/types/codepurify.config.types';

export interface EntityDiscoveryOptions {
  /** Pattern to match entity config files */
  pattern?: string;
  /** Include subdirectories */
  recursive?: boolean;
  /** Filter by entity key pattern */
  keyPattern?: RegExp;
}

export interface DiscoveredEntity {
  /** Relative path from project root */
  path: string;
  /** Absolute file path */
  absolutePath: string;
  /** Entity key extracted from filename/class name */
  key: string;
  /** Group key from directory structure */
  groupKey?: string;
}

export class EntityDiscovery {
  constructor(private readonly runtime: CodepurifyRuntime) {}

  /**
   * Discovers entity configuration files based on global config.
   *
   * @param globalConfig - Resolved global configuration
   * @param options - Discovery options
   * @returns Array of discovered entity files
   */
  async discoverEntityConfigs(globalConfig: ResolvedCodepurifyConfig, options: EntityDiscoveryOptions = {}): Promise<DiscoveredEntity[]> {
    const { pattern = '**/*.ts', recursive = true, keyPattern } = options;

    const entitiesDir = resolve(globalConfig.rootDir, globalConfig.entitiesDir);
    // Convert Windows backslashes to forward slashes for fast-glob compatibility
    const normalizedEntitiesDir = entitiesDir.replace(/\\/g, '/');
    const searchPattern = recursive ? `${normalizedEntitiesDir}/${pattern}` : `${normalizedEntitiesDir}/${pattern}`;

    console.debug(`Entity discovery - entitiesDir: ${entitiesDir}`);
    console.debug(`Entity discovery - normalizedEntitiesDir: ${normalizedEntitiesDir}`);
    console.debug(`Entity discovery - searchPattern: ${searchPattern}`);

    try {
      const files = await fastGlob(searchPattern, {
        absolute: true,
        onlyFiles: true,
        ignore: ['**/node_modules/**', '**/dist/**'],
      });

      console.debug(`Entity discovery - found files: ${files.length}`, files);

      const entities: DiscoveredEntity[] = [];

      for (const absolutePath of files) {
        const entityInfo = this.getEntityDiscoveryInfo(absolutePath, entitiesDir);

        // Apply key pattern filter if provided
        if (keyPattern && !keyPattern.test(entityInfo.key)) {
          continue;
        }

        entities.push(entityInfo);
      }

      return entities.sort((a, b) => a.key.localeCompare(b.key));
    } catch (error) {
      throw new Error(`Failed to discover entity configs: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * Gets entity discovery information from file path.
   *
   * @param filePath - Absolute file path
   * @param entitiesDir - Base entities directory
   * @returns Entity discovery information
   */
  private getEntityDiscoveryInfo(filePath: string, entitiesDir: string): DiscoveredEntity {
    const relativePath = relative(entitiesDir, filePath).replace(/\\/g, '/');
    const parts = relativePath.split('/');

    const filename = parts.at(-1)!;
    const key = filename.replace(/\.ts$/, '').replace(/-/g, '_'); // Convert kebab to underscore

    const groupKey = parts.length > 1 ? parts[0] : undefined;

    return {
      path: relativePath,
      absolutePath: filePath,
      key,
      groupKey,
    };
  }
}
