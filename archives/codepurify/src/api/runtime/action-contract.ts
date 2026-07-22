/**
 * Codepurify Action Contract
 *
 * Defines the standard shape for all Codepurify actions.
 * Provides a unified interface for action execution with consistent error handling.
 */

import { performance } from 'node:perf_hooks';

import type { BaseCodepurifyResult } from '@/api/types';
import type { CodepurifyRuntime } from './codepurify-runtime';
import { CodepurifyError, CodepurifyErrorCode } from '@/core/errors';

/**
 * Standard contract for all Codepurify actions.
 *
 * Every action must define:
 * - name: Human-readable action name
 * - defaults: Default result values for failure cases
 * - run: Core action logic that returns partial result data
 */
export interface CodepurifyAction<TOptions, TResult extends BaseCodepurifyResult> {
  /**
   * Human-readable name for the action (used in error messages).
   */
  name: string;

  /**
   * Returns default values for the result when action fails.
   * This ensures consistent failure result structure.
   */
  defaults(options: TOptions): Omit<TResult, keyof BaseCodepurifyResult>;

  /**
   * Core action logic.
   * Returns partial result data (without BaseCodepurifyResult fields).
   */
  run(runtime: CodepurifyRuntime, options: TOptions): Promise<Omit<TResult, keyof BaseCodepurifyResult>>;
}

/**
 * Normalizes unknown errors into CodepurifyError instances.
 *
 * @param actionName - Name of the action for error context
 * @param error - Unknown error to normalize
 * @returns Normalized CodepurifyError
 */
export function normalizeCodepurifyError(actionName: string, error: unknown): CodepurifyError {
  if (error instanceof CodepurifyError) {
    return error;
  }

  // Create a new CodepurifyError with the original error as cause
  const normalizedError = new CodepurifyError(CodepurifyErrorCode.GENERATION_FAILED, `${actionName} failed`);

  // Set the cause property directly for proper error reporting
  (normalizedError as any).cause = error;

  return normalizedError;
}

/**
 * Executes a Codepurify action with standardized timing, error handling, and result structure.
 *
 * @param runtime - Codepurify runtime instance
 * @param action - Action contract to execute
 * @param options - Action options
 * @returns Complete action result with timing and error handling
 */
export async function executeAction<TOptions, TResult extends BaseCodepurifyResult>(
  runtime: CodepurifyRuntime,
  action: CodepurifyAction<TOptions, TResult>,
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
    const normalized = normalizeCodepurifyError(action.name, error);

    return {
      success: false,
      warnings: [],
      errors: [normalized],
      durationMs: performance.now() - start,
      ...action.defaults(options),
    } as unknown as TResult;
  }
}
