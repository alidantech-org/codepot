/**
 * Codepurify Public API Facade
 *
 * Thin public facade that delegates to specialized action handlers.
 * Provides a clean, minimal public interface while keeping implementation
 * details organized in separate action modules.
 */
import { generateAction, initAction, rollbackAction } from './actions';
import * as T from './types';
import { executeAction } from './runtime';
import { CodepurifyRuntime } from './runtime/codepurify-runtime';

/**
 * Main Codepurify execution class.
 *
 * Provides a reusable, embeddable runtime for Codepurify operations.
 * Can be used by CLI, VS Code extensions, UI integrations, and tests.
 *
 * This class acts as a thin facade - all actual implementation logic
 * is delegated to specialized action handlers.
 */
export class Codepurify {
  private readonly runtime: CodepurifyRuntime;

  constructor(options: T.CodepurifyOptions = {}) {
    this.runtime = new CodepurifyRuntime(options);
  }

  /**
   * Public file-management contract.
   *
   * Exposes safe read/write/info/rollback operations without exposing runtime internals.
   */
  get files() {
    return this.runtime.files;
  }

  /**
   * Initialize Codepurify configuration and template registry files.
   */
  async init(options: T.InitOptions = {}): Promise<T.InitResult> {
    return await executeAction(this.runtime, initAction, options);
  }

  /**
   * Generate artifacts from entity configurations.
   */
  async generate(options: T.GenerateOptions = {}): Promise<T.GenerateResult> {
    return await executeAction(this.runtime, generateAction, options);
  }

  /**
   * Rollback files from backup sessions.
   */
  async rollback(options: T.RollbackOptions = {}): Promise<T.RollbackResult> {
    return await executeAction(this.runtime, rollbackAction, options);
  }

  /**
   * Check configuration and validate setup.
   */
  async check(options: T.CheckOptions = {}): Promise<T.CheckResult> {
    // TODO: Implement checkAction
    throw new Error('check action not yet implemented');
  }

  /**
   * Clean generated files and artifacts.
   */
  async clean(options: T.CleanOptions = {}): Promise<T.CleanResult> {
    // TODO: Implement cleanAction
    throw new Error('clean action not yet implemented');
  }

  /**
   * Preview what would be generated without writing files.
   */
  async preview(options: T.PreviewOptions = {}): Promise<T.PreviewResult> {
    // TODO: Implement previewAction
    throw new Error('preview action not yet implemented');
  }

  /**
   * Watch for file changes and regenerate automatically.
   */
  async watch(options: T.WatchOptions = {}): Promise<void> {
    // TODO: Implement watchAction
    throw new Error('watch action not yet implemented');
  }

  /**
   * Stop the file watcher.
   */
  async stop(): Promise<void> {
    return this.runtime.stopWatcher();
  }
}
