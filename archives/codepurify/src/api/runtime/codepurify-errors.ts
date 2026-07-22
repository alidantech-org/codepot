/**
 * Codepurify Error Helpers
 *
 * Centralized error wrapping and handling utilities.
 */

import { CodepurifyError, CodepurifyErrorCode } from '@/core/errors';

/**
 * Wrap unknown errors in CodepurifyError with consistent message format.
 */
export function wrapCodepurifyError(actionName: string, error: unknown): CodepurifyError {
  if (error instanceof CodepurifyError) {
    return error;
  }

  return new CodepurifyError(CodepurifyErrorCode.GENERATION_FAILED, `${actionName} failed`, { cause: error });
}
