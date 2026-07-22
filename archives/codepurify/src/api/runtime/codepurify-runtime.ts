/**
 * codepot Runtime
 *
 * Shared runtime services and dependencies for codepot operations.
 */

import { resolve } from 'node:path';
import { watch as chokidarWatch, type FSWatcher } from 'chokidar';

import { debug } from '@/core/logger';
import { codepotFiles } from '@/core/files';
import { codepotAssets } from './codepot-assets';
import type { codepotOptions } from '@/api/types';

/**
 * Shared runtime dependencies for codepot operations.
 *
 * Provides initialized managers and shared services that actions can reuse.
 * This eliminates repeated initialization and provides a central place for
 * managing shared resources like file watchers.
 */
export class codepotRuntime {
  readonly cwd: string;
  readonly configPath?: string;
  readonly templatesPath?: string;
  public readonly files: codepotFiles;
  public readonly assets: codepotAssets;
  watcher?: FSWatcher;

  constructor(options: codepotOptions = {}) {
    this.cwd = resolve(options.cwd ?? process.cwd());
    this.configPath = options.configPath;
    this.templatesPath = options.templatesPath;

    // Initialize files module
    this.files = new codepotFiles({
      rootDir: this.cwd,
      dbPath: '.codepot/files.json',
      backupDir: '.codepot/backups',
    });

    // Initialize assets module
    this.assets = new codepotAssets();

    debug(`codepot runtime initialized in: ${this.cwd}`);
  }

  /**
   * Stop the active file watcher if running.
   */
  async stopWatcher(): Promise<void> {
    if (!this.watcher) return;

    await this.watcher.close();
    this.watcher = undefined;
    debug('File watcher stopped');
  }

  /**
   * Create a new file watcher with the given patterns and options.
   */
  createWatcher(patterns: string[], options: any): FSWatcher {
    // Stop existing watcher if any
    if (this.watcher) {
      this.stopWatcher();
    }

    this.watcher = chokidarWatch(patterns, options);
    return this.watcher;
  }
}
