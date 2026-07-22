/**
 * Codepurify Shell Utilities
 *
 * Provides shell command execution using execa.
 * Includes command existence checking and result handling.
 */

import { execa } from 'execa';

/**
 * Options for running shell commands
 */
export interface RunCommandOptions {
  /** Working directory */
  cwd?: string;
  /** Environment variables */
  env?: NodeJS.ProcessEnv;
  /** Whether to reject on non-zero exit code */
  reject?: boolean;
  /** Standard I/O handling */
  stdio?: 'inherit' | 'pipe';
}

/**
 * Result of running a shell command
 */
export interface RunCommandResult {
  /** Command that was run */
  command: string;
  /** Exit code */
  exitCode: number;
  /** Standard output */
  stdout: string;
  /** Standard error */
  stderr: string;
}

/**
 * Error thrown when shell commands fail
 */
export class ShellError extends Error {
  constructor(
    message: string,
    public result: RunCommandResult,
    public cause?: Error,
  ) {
    super(message);
    this.name = 'ShellError';
  }
}

/**
 * Runs a shell command with options
 *
 * @param command - Command to run
 * @param args - Command arguments
 * @param options - Run options
 * @returns Command execution result
 * @throws ShellError if command fails and reject is true
 */
export async function runCommand(command: string, args?: string[], options: RunCommandOptions = {}): Promise<RunCommandResult> {
  const { cwd = process.cwd(), env, reject = false, stdio = 'pipe' } = options;

  try {
    const result = await execa(command, args || [], {
      cwd,
      env: { ...process.env, ...env },
      stdio,
      reject: false, // We'll handle rejection ourselves
    });

    const commandResult: RunCommandResult = {
      command: `${command}${args && args.length > 0 ? ` ${args.join(' ')}` : ''}`,
      exitCode: result.exitCode || 0,
      stdout: result.stdout || '',
      stderr: result.stderr || '',
    };

    // If reject is true and command failed, throw error
    if (reject && commandResult.exitCode !== 0) {
      throw new ShellError(`Command failed with exit code ${commandResult.exitCode}: ${commandResult.command}`, commandResult);
    }

    return commandResult;
  } catch (error) {
    // If it's already a ShellError, re-throw it
    if (error instanceof ShellError) {
      throw error;
    }

    // Otherwise, wrap it in a ShellError
    const commandStr = `${command}${args && args.length > 0 ? ` ${args.join(' ')}` : ''}`;
    throw new ShellError(
      `Failed to execute command: ${commandStr}`,
      {
        command: commandStr,
        exitCode: -1,
        stdout: '',
        stderr: (error as Error).message,
      },
      error as Error,
    );
  }
}

/**
 * Checks if a command exists in the system PATH
 *
 * @param command - Command to check
 * @returns True if command exists
 */
export async function commandExists(command: string): Promise<boolean> {
  try {
    // Use 'which' on Unix-like systems, 'where' on Windows
    const checkCommand = process.platform === 'win32' ? 'where' : 'which';

    const result = await runCommand(checkCommand, [command], {
      stdio: 'pipe',
      reject: false,
    });

    return result.exitCode === 0;
  } catch {
    return false;
  }
}
