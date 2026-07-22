/**
 * Codepurify Execution Types
 *
 * Core types for the Codepurify execution API.
 */

/**
 * Main Codepurify execution options.
 */
export interface CodepurifyOptions {
  /**
   * Working directory for Codepurify execution.
   */
  cwd?: string;

  /**
   * Path to the global config file.
   */
  configPath?: string;

  /**
   * Path to the templates registry file.
   */
  templatesPath?: string;
}

/**
 * Generate execution options.
 */
export interface GenerateOptions {
  /**
   * Specific entity to generate.
   */
  entity?: string;

  /**
   * Specific entity group to generate.
   */
  group?: string;

  /**
   * Specific templates to run.
   */
  templates?: string[];

  /**
   * Run in dry-run mode without writing files.
   */
  dryRun?: boolean;

  /**
   * Only generate changed files.
   */
  changedOnly?: boolean;

  /**
   * Force regeneration of all files.
   */
  force?: boolean;
}

/**
 * Check execution options.
 */
export interface CheckOptions {
  /**
   * Specific entity to check.
   */
  entity?: string;

  /**
   * Specific entity group to check.
   */
  group?: string;

  /**
   * Validate templates only.
   */
  templatesOnly?: boolean;
}

/**
 * Clean execution options.
 */
export interface CleanOptions {
  /**
   * Clean specific entity only.
   */
  entity?: string;

  /**
   * Clean specific entity group only.
   */
  group?: string;

  /**
   * Keep manifest file.
   */
  keepManifest?: boolean;

  /**
   * Keep backup files.
   */
  keepBackups?: boolean;
}

/**
 * Rollback execution options.
 */
export interface RollbackOptions {
  /**
   * Rollback to specific backup ID.
   */
  backupId?: string;

  /**
   * Rollback to specific timestamp.
   */
  timestamp?: string;

  /**
   * Force rollback even if validation fails.
   */
  force?: boolean;
}

/**
 * Preview execution options.
 */
export interface PreviewOptions {
  /**
   * Preview specific entity only.
   */
  entity?: string;

  /**
   * Preview specific entity group only.
   */
  group?: string;

  /**
   * Show file contents in preview.
   */
  showContents?: boolean;

  /**
   * Limit number of files to preview.
   */
  limit?: number;
}

/**
 * Init execution options.
 */
export interface InitOptions {
  /**
   * Force overwrite existing files.
   */
  force?: boolean;

  /**
   * Run in dry-run mode without writing files.
   */
  dryRun?: boolean;

  /**
   * Show debug information for troubleshooting.
   */
  debug?: boolean;
}

/**
 * Watch execution options.
 */
export interface WatchOptions {
  /**
   * Debounce time in milliseconds for file changes.
   */
  debounceMs?: number;

  /**
   * Generate files on watch start.
   */
  generateOnStart?: boolean;

  /**
   * Only regenerate changed files.
   */
  changedOnly?: boolean;

  /**
   * Callback for watch events.
   */
  onChange?: (event: CodepurifyWatchEvent) => Promise<void>;
}

/**
 * Watch event types.
 */
export interface CodepurifyWatchEvent {
  /**
   * Type of change event.
   */
  type: 'entity' | 'template' | 'config' | 'global';

  /**
   * Path that changed.
   */
  path: string;

  /**
   * Event type.
   */
  eventType: 'added' | 'changed' | 'deleted';

  /**
   * Timestamp of the event.
   */
  timestamp: Date;
}
