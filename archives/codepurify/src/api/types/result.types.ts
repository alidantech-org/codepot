/**
 * Codepurify Result Types
 *
 * Structured result objects for all Codepurify operations.
 */

import type { CodepurifyError } from '@/core/errors';

/**
 * Base result interface for all operations.
 */
export interface BaseCodepurifyResult {
  /**
   * Whether the operation was successful.
   */
  success: boolean;

  /**
   * Warnings generated during the operation.
   */
  warnings: string[];

  /**
   * Errors generated during the operation.
   */
  errors: CodepurifyError[];

  /**
   * Operation duration in milliseconds.
   */
  durationMs: number;
}

/**
 * Result for a generated file.
 */
export interface GeneratedFileResult {
  /**
   * Relative path to the generated file.
   */
  path: string;

  /**
   * Action performed on the file.
   */
  action: 'created' | 'updated' | 'unchanged' | 'deleted';

  /**
   * Name of the template that generated the file.
   */
  templateName: string;

  /**
   * File size in bytes.
   */
  size: number;

  /**
   * Whether the file content changed.
   */
  changed: boolean;
}

/**
 * Result for generate operation.
 */
export interface GenerateResult extends BaseCodepurifyResult {
  /**
   * Files that were generated or processed.
   */
  generatedFiles: GeneratedFileResult[];

  /**
   * Number of entities processed.
   */
  entitiesProcessed: number;

  /**
   * Number of templates executed.
   */
  templatesExecuted: number;

  /**
   * Whether this was a dry run.
   */
  dryRun: boolean;
}

/**
 * Result for check operation.
 */
export interface CheckResult extends BaseCodepurifyResult {
  /**
   * Configuration validation results.
   */
  configValidation: {
    valid: boolean;
    errors: string[];
  };

  /**
   * Template validation results.
   */
  templateValidation: {
    valid: boolean;
    errors: string[];
  };

  /**
   * Entity validation results.
   */
  entityValidation: {
    valid: boolean;
    errors: string[];
  };

  /**
   * Number of entities checked.
   */
  entitiesChecked: number;

  /**
   * Number of templates checked.
   */
  templatesChecked: number;
}

/**
 * Result for clean operation.
 */
export interface CleanResult extends BaseCodepurifyResult {
  /**
   * Files that were cleaned.
   */
  cleanedFiles: string[];

  /**
   * Number of files cleaned.
   */
  filesCleaned: number;

  /**
   * Whether manifest was cleaned.
   */
  manifestCleaned: boolean;

  /**
   * Number of backups cleaned.
   */
  backupsCleaned: number;
}

/**
 * Result for rollback operation.
 */
export interface RollbackResult extends BaseCodepurifyResult {
  /**
   * ID of the backup that was rolled back.
   */
  backupId: string;

  /**
   * Timestamp of the backup.
   */
  backupTimestamp: Date;

  /**
   * Files that were restored.
   */
  restoredFiles: string[];

  /**
   * Number of files restored.
   */
  filesRestored: number;

  /**
   * Whether manifest was restored.
   */
  manifestRestored: boolean;
}

/**
 * Result for init operation.
 */
export interface InitResult extends BaseCodepurifyResult {
  /**
   * Files that were created.
   */
  createdFiles: GeneratedFileResult[];

  /**
   * Files that were skipped (already existed).
   */
  skippedFiles: string[];
}

/**
 * Result for preview operation.
 */
export interface PreviewResult extends BaseCodepurifyResult {
  /**
   * Files that would be generated.
   */
  previewFiles: PreviewFileResult[];

  /**
   * Number of files previewed.
   */
  filesPreviewed: number;

  /**
   * Whether file contents are included.
   */
  includesContents: boolean;
}

/**
 * Result for a previewed file.
 */
export interface PreviewFileResult extends GeneratedFileResult {
  /**
   * File content (if requested).
   */
  content?: string;

  /**
   * File hash.
   */
  hash: string;
}
