/**
 * codepot Action Contract
 *
 * Defines the standard shape for all codepot actions.
 * Provides a unified interface for action execution with consistent error handling.
 */

import { performance } from 'node:perf_hooks';

import type { BasecodepotResult } from '@/api/types';
import type { codepotRuntime } from './codepot-runtime';
import { codepotError, codepotErrorCode } from '@/core/errors';

/**
 * Standard contract for all codepot actions.
 *
 * Every action must define:
 * - name: Human-readable action name
 * - defaults: Default result values for failure cases
 * - run: Core action logic that returns partial result data
 */
export interface codepotAction<TOptions, TResult extends BasecodepotResult> {
  /**
   * Human-readable name for the action (used in error messages).
   */
  name: string;

  /**
   * Returns default values for the result when action fails.
   * This ensures consistent failure result structure.
   */
  defaults(options: TOptions): Omit<TResult, keyof BasecodepotResult>;

  /**
   * Core action logic.
   * Returns partial result data (without BasecodepotResult fields).
   */
  run(runtime: codepotRuntime, options: TOptions): Promise<Omit<TResult, keyof BasecodepotResult>>;
}

/**
 * Normalizes unknown errors into codepotError instances.
 *
 * @param actionName - Name of the action for error context
 * @param error - Unknown error to normalize
 * @returns Normalized codepotError
 */
export function normalizecodepotError(actionName: string, error: unknown): codepotError {
  if (error instanceof codepotError) {
    return error;
  }

  // Create a new codepotError with the original error as cause
  const normalizedError = new codepotError(codepotErrorCode.GENERATION_FAILED, `${actionName} failed`);

  // Set the cause property directly for proper error reporting
  (normalizedError as any).cause = error;

  return normalizedError;
}

/**
 * Executes a codepot action with standardized timing, error handling, and result structure.
 *
 * @param runtime - codepot runtime instance
 * @param action - Action contract to execute
 * @param options - Action options
 * @returns Complete action result with timing and error handling
 */
export async function executeAction<TOptions, TResult extends BasecodepotResult>(
  runtime: codepotRuntime,
  action: codepotAction<TOptions, TResult>,
  options: TOptions,
): Promise<TResult> {
  const start = performance.now();

  try {
    const data = await action.run(runtime, options);

    return {
      success: true,
      warnings: [],
      errors: [],
      durationMs: performance.now() - start,
      ...data,
    } as unknown as TResult;
  } catch (error) {
    const normalized = normalizecodepotError(action.name, error);

    return {
      success: false,
      warnings: [],
      errors: [normalized],
      durationMs: performance.now() - start,
      ...action.defaults(options),
    } as unknown as TResult;
  }
}
