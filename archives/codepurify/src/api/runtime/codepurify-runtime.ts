/**
 * Codepurify Runtime
 *
 * Shared runtime services and dependencies for Codepurify operations.
 */

import { resolve } from 'node:path';
import { watch as chokidarWatch, type FSWatcher } from 'chokidar';

import { debug } from '@/core/logger';
import { CodepurifyFiles } from '@/core/files';
import { CodepurifyAssets } from './codepurify-assets';
import type { CodepurifyOptions } from '@/api/types';

/**
 * Shared runtime dependencies for Codepurify operations.
 *
 * Provides initialized managers and shared services that actions can reuse.
 * This eliminates repeated initialization and provides a central place for
 * managing shared resources like file watchers.
 */
export class CodepurifyRuntime {
  readonly cwd: string;
  readonly configPath?: string;
  readonly templatesPath?: string;
  public readonly files: CodepurifyFiles;
  public readonly assets: CodepurifyAssets;
  watcher?: FSWatcher;

  constructor(options: CodepurifyOptions = {}) {
    this.cwd = resolve(options.cwd ?? process.cwd());
    this.configPath = options.configPath;
    this.templatesPath = options.templatesPath;

    // Initialize files module
    this.files = new CodepurifyFiles({
      rootDir: this.cwd,
      dbPath: '.codepurify/files.json',
      backupDir: '.codepurify/backups',
    });

    // Initialize assets module
    this.assets = new CodepurifyAssets();

    debug(`Codepurify runtime initialized in: ${this.cwd}`);
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
