/**
 * Codepurify Glob Utilities
 *
 * Provides file system operations using fast-glob for pattern matching.
 * Includes directory operations and file existence checks.
 */

import fastGlob from 'fast-glob';
import { access, stat, mkdir, rm } from 'node:fs/promises';
import { constants } from 'node:fs';

/**
 * Options for glob file operations
 */
export interface GlobFilesOptions {
  /** Working directory */
  cwd: string;
  /** Return absolute paths */
  absolute?: boolean;
  /** Patterns to ignore */
  ignore?: string[];
}

/**
 * Error thrown when file operations fail
 */
export class GlobError extends Error {
  constructor(
    message: string,
    public cause?: Error,
  ) {
    super(message);
    this.name = 'GlobError';
  }
}

/**
 * Finds files matching the given patterns
 *
 * @param patterns - Glob pattern(s) to match
 * @param options - Glob options
 * @returns Array of matching file paths (sorted)
 */
export async function globFiles(patterns: string | string[], options: GlobFilesOptions): Promise<string[]> {
  try {
    const { cwd, absolute = false, ignore = [] } = options;

    // Default ignore patterns
    const defaultIgnore = ['**/node_modules/**', '**/dist/**', '**/.git/**'];
    const allIgnore = [...defaultIgnore, ...ignore];

    const results = await fastGlob(patterns, {
      cwd,
      absolute,
      ignore: allIgnore,
      onlyFiles: true, // Only return files, not directories
      dot: false, // Ignore dot files by default
    });

    // Return sorted results
    return results.sort();
  } catch (error) {
    throw new GlobError(`Failed to glob files: ${patterns}`, error as Error);
  }
}

/**
 * Checks if a file exists
 *
 * @param filePath - Path to the file
 * @returns True if file exists
 */
export async function fileExists(filePath: string): Promise<boolean> {
  try {
    await access(filePath, constants.F_OK);
    const stats = await stat(filePath);
    return stats.isFile();
  } catch {
    return false;
  }
}

/**
 * Checks if a directory exists
 *
 * @param dirPath - Path to the directory
 * @returns True if directory exists
 */
export async function directoryExists(dirPath: string): Promise<boolean> {
  try {
    await access(dirPath, constants.F_OK);
    const stats = await stat(dirPath);
    return stats.isDirectory();
  } catch {
    return false;
  }
}

/**
 * Ensures a directory exists, creating it if necessary
 *
 * @param dirPath - Path to the directory
 * @throws GlobError if directory creation fails
 */
export async function ensureDirectory(dirPath: string): Promise<void> {
  try {
    await mkdir(dirPath, { recursive: true });
  } catch (error) {
    throw new GlobError(`Failed to ensure directory: ${dirPath}`, error as Error);
  }
}

/**
 * Removes a directory and all its contents
 *
 * @param dirPath - Path to the directory to remove
 * @throws GlobError if directory removal fails
 */
export async function removeDirectory(dirPath: string): Promise<void> {
  try {
    await rm(dirPath, { recursive: true, force: true });
  } catch (error) {
    throw new GlobError(`Failed to remove directory: ${dirPath}`, error as Error);
  }
}
