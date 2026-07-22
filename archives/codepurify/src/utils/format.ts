/**
 * Codepurify Format Utilities
 *
 * Provides code formatting helpers for prettier, eslint, and TypeScript.
 * Uses shell utilities to run formatting commands.
 */

import { runCommand } from './shell';

/**
 * Error thrown when formatting operations fail
 */
export class FormatError extends Error {
  constructor(
    message: string,
    public cause?: Error,
  ) {
    super(message);
    this.name = 'FormatError';
  }
}

/**
 * Formats files with Prettier
 *
 * @param filePaths - Array of file paths to format
 * @param cwd - Working directory
 * @throws FormatError if prettier command fails
 */
export async function formatWithPrettier(filePaths: string[], cwd: string): Promise<void> {
  // If no files provided, return immediately
  if (!filePaths || filePaths.length === 0) {
    return;
  }

  try {
    const result = await runCommand('npx', ['prettier', '--write', ...filePaths], {
      cwd,
      reject: true,
      stdio: 'pipe',
    });

    // Check if prettier actually made any changes
    if (result.stderr && result.stderr.includes('error')) {
      throw new FormatError(`Prettier errors: ${result.stderr}`);
    }
  } catch (error) {
    if (error instanceof FormatError) {
      throw error;
    }
    throw new FormatError(`Failed to format files with prettier`, error as Error);
  }
}

/**
 * Runs TypeScript compiler check
 *
 * @param cwd - Working directory
 * @throws FormatError if typecheck fails
 */
export async function runTypecheck(cwd: string): Promise<void> {
  try {
    await runCommand('npx', ['tsc', '--noEmit'], {
      cwd,
      reject: true,
      stdio: 'pipe',
    });

    // TypeScript compiler outputs errors to stderr even when not failing
    // We only care about the exit code, which is handled by reject: true
  } catch (error) {
    if (error instanceof FormatError) {
      throw error;
    }

    // Extract error details from shell error if available
    let errorMessage = 'TypeScript compilation failed';
    if (error && typeof error === 'object' && 'result' in error) {
      const shellError = error as any;
      if (shellError.result?.stderr) {
        errorMessage += `: ${shellError.result.stderr}`;
      }
    }

    throw new FormatError(errorMessage, error as Error);
  }
}

/**
 * Runs ESLint on files
 *
 * @param filePaths - Array of file paths to lint
 * @param cwd - Working directory
 * @throws FormatError if eslint command fails
 */
export async function runEslint(filePaths: string[], cwd: string): Promise<void> {
  // If no files provided, return immediately
  if (!filePaths || filePaths.length === 0) {
    return;
  }

  try {
    await runCommand('npx', ['eslint', ...filePaths], {
      cwd,
      reject: true,
      stdio: 'pipe',
    });

    // ESLint outputs warnings to stderr even when not failing
    // We only care about the exit code, which is handled by reject: true
  } catch (error) {
    if (error instanceof FormatError) {
      throw error;
    }

    // Extract error details from shell error if available
    let errorMessage = 'ESLint failed';
    if (error && typeof error === 'object' && 'result' in error) {
      const shellError = error as any;
      if (shellError.result?.stderr) {
        errorMessage += `: ${shellError.result.stderr}`;
      }
    }

    throw new FormatError(errorMessage, error as Error);
  }
}
