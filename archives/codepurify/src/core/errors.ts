/**
 * codepot Error System
 *
 * Provides structured error handling with error codes and detailed information.
 * All codepot errors should extend from codepotError for consistent handling.
 */

/**
 * Error codes for different types of codepot errors
 */
export enum codepotErrorCode {
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
 * Base error class for all codepot errors
 */
export class codepotError extends Error {
  constructor(
    public code: codepotErrorCode,
    message: string,
    public details?: Record<string, unknown>,
  ) {
    super(message);
    this.name = 'codepotError';

    // Maintains proper stack trace for where our error was thrown
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, codepotError);
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
 * Creates a codepotError with the given code and message
 *
 * @param code - Error code
 * @param message - Error message
 * @param details - Optional error details
 * @returns codepotError instance
 */
export function createcodepotError(code: codepotErrorCode, message: string, details?: Record<string, unknown>): codepotError {
  return new codepotError(code, message, details);
}

/**
 * Type guard to check if an error is a codepotError
 *
 * @param error - Error to check
 * @returns True if error is a codepotError
 */
export function iscodepotError(error: unknown): error is codepotError {
  return error instanceof codepotError;
}
