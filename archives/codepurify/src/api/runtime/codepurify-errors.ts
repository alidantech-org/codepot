/**
 * codepot Error Helpers
 *
 * Centralized error wrapping and handling utilities.
 */

import { codepotError, codepotErrorCode } from '@/core/errors';

/**
 * Wrap unknown errors in codepotError with consistent message format.
 */
export function wrapcodepotError(actionName: string, error: unknown): codepotError {
  if (error instanceof codepotError) {
    return error;
  }

  return new codepotError(codepotErrorCode.GENERATION_FAILED, `${actionName} failed`, { cause: error });
}
