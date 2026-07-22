/**
 * Rollback Action
 *
 * Restores files from a Codepurify backup session.
 *
 * Pipeline:
 *
 * backup session selection
 *   ↓
 * file restoration
 *   ↓
 * generated file cleanup
 *   ↓
 * manifest update
 */

import type { RollbackOptions, RollbackResult } from '@/api/types';
import type { CodepurifyAction } from '@/api/runtime/action-contract';

import { debug, info, success } from '@/core/logger';

import { ROLLBACK_ACTION, ROLLBACK_LOG_MESSAGES } from '@/api/constants';

export const rollbackAction: CodepurifyAction<RollbackOptions, RollbackResult> = {
  name: ROLLBACK_ACTION.name,

  defaults: (options) => ({
    backupId: options.backupId ?? 'latest',
    backupTimestamp: new Date(),
    restoredFiles: [],
    filesRestored: 0,
    manifestRestored: false,
  }),

  async run(runtime, options) {
    info(ROLLBACK_LOG_MESSAGES.starting);

    /**
     * STEP 1
     * -----------------------------------------
     * Select and execute rollback operation.
     *
     * If a specific backup ID is provided, rollback to that session.
     * Otherwise, rollback to the latest available backup session.
     *
     * Expected:
     * - backup session validation
     * - file restoration from backups
     * - cleanup of generated files
     * - manifest updates
     */

    const rollbackResult = options.backupId ? await runtime.files.rollback(options.backupId) : await runtime.files.rollbackLatest();

    /**
     * STEP 2
     * -----------------------------------------
     * Extract rollback results.
     *
     * The rollback operation returns:
     * - restoredFiles: files that were restored from backup
     * - deletedFiles: generated files that were deleted
     * - skippedFiles: files that were skipped (no changes needed)
     */

    const restoredFiles = rollbackResult.restoredFiles;
    const deletedFiles = rollbackResult.deletedFiles ?? [];
    const skippedFiles = rollbackResult.skippedFiles ?? [];

    /**
     * STEP 3
     * -----------------------------------------
     * Log rollback statistics.
     *
     * Provide detailed feedback on what was done during rollback.
     */

    debug(ROLLBACK_LOG_MESSAGES.restored(restoredFiles.length));
    debug(ROLLBACK_LOG_MESSAGES.deleted(deletedFiles.length));
    debug(ROLLBACK_LOG_MESSAGES.skipped(skippedFiles.length));

    /**
     * STEP 4
     * -----------------------------------------
     * Finalize rollback operation.
     *
     * Return structured result with rollback details.
     */

    success(ROLLBACK_LOG_MESSAGES.completed(rollbackResult.sessionId));

    return {
      backupId: rollbackResult.sessionId,
      backupTimestamp: new Date(),
      restoredFiles,
      filesRestored: restoredFiles.length,
      manifestRestored: true,
    };
  },
};
