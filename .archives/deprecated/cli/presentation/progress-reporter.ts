// cli/presentation/progress-reporter.ts

import pc from 'picocolors';

import type { AppProgressEvent, AppProgressReporter } from '@/app/emit-ir';
import type { Logger } from '@/utils/logger';

// ============================================================================
// FACTORY
// ============================================================================

/**
 * Creates a CLI progress reporter for app workflows.
 */
export function createCliProgressReporter(logger: Logger): AppProgressReporter {
  return {
    report(event: AppProgressEvent): void {
      if (event.type === 'success') {
        logger.success(event.message);
        return;
      }

      if (event.type === 'write' && event.file !== undefined) {
        logger.info(event.message.replace(event.file, pc.gray(event.file)));
        return;
      }

      logger.info(event.message);
    },
  };
}
