/**
 * Codepurify Error System
 *
 * Provides structured error handling with error codes and detailed information.
 * All Codepurify errors should extend from CodepurifyError for consistent handling.
 */

/**
 * Error codes for different types of Codepurify errors
 */
export enum CodepurifyErrorCode {
  CONFIG_NOT_FOUND = 'CONFIG_NOT_FOUND',
  CONFIG_INVALID = 'CONFIG_INVALID',
  FILE_NOT_FOUND = 'FILE_NOT_FOUND',
  FILE_WRITE_FAILED = 'FILE_WRITE_FAILED',
  MANIFEST_INVALID = 'MANIFEST_INVALID',
  GENERATION_FAILED = 'GENERATION_FAILED',
  BACKUP_FAILED = 'BACKUP_FAILED',
  ROLLBACK_FAILED = 'ROLLBACK_FAILED',
  VALIDATION_FAILED = 'VALIDATION_FAILED',
  COMMAND_FAILED = 'COMMAND_FAILED',
  TEMPLATE_NOT_FOUND = 'TEMPLATE_NOT_FOUND',
}

/**
 * Base error class for all Codepurify errors
 */
export class CodepurifyError extends Error {
  constructor(
    public code: CodepurifyErrorCode,
    message: string,
    public details?: Record<string, unknown>,
  ) {
    super(message);
    this.name = 'CodepurifyError';

    // Maintains proper stack trace for where our error was thrown
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, CodepurifyError);
    }
  }

  /**
   * Returns a JSON representation of the error
   */
  toJSON() {
    return {
      name: this.name,
      code: this.code,
      message: this.message,
      details: this.details,
      stack: this.stack,
    };
  }

  /**
   * Returns a formatted error message
   */
  toString(): string {
    let result = `${this.name} [${this.code}]: ${this.message}`;

    if (this.details) {
      const detailsStr = Object.entries(this.details)
        .map(([key, value]) => `${key}=${JSON.stringify(value)}`)
        .join(', ');
      result += ` (${detailsStr})`;
    }

    return result;
  }
}

/**
 * Creates a CodepurifyError with the given code and message
 *
 * @param code - Error code
 * @param message - Error message
 * @param details - Optional error details
 * @returns CodepurifyError instance
 */
export function createCodepurifyError(code: CodepurifyErrorCode, message: string, details?: Record<string, unknown>): CodepurifyError {
  return new CodepurifyError(code, message, details);
}

/**
 * Type guard to check if an error is a CodepurifyError
 *
 * @param error - Error to check
 * @returns True if error is a CodepurifyError
 */
export function isCodepurifyError(error: unknown): error is CodepurifyError {
  return error instanceof CodepurifyError;
}
