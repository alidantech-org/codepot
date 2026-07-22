/**
 * Codepurify Path Utilities
 *
 * Provides path manipulation helpers with cross-platform support.
 * Normalizes Windows paths to POSIX when returning relative paths.
 */

import { resolve, relative, dirname, basename, extname, join } from 'node:path';

/**
 * Converts a path to POSIX format (forward slashes)
 *
 * @param input - Path to convert
 * @returns POSIX-formatted path
 */
export function toPosixPath(input: string): string {
  return input.replace(/\\/g, '/');
}

/**
 * Normalizes a path and converts to POSIX format
 *
 * @param input - Path to normalize
 * @returns Normalized POSIX path
 */
export function normalizePath(input: string): string {
  return toPosixPath(resolve(input));
}

/**
 * Resolves a path relative to a root directory
 *
 * @param rootDir - Root directory
 * @param value - Path value to resolve
 * @returns Resolved absolute path
 */
export function resolveFromRoot(rootDir: string, value: string): string {
  return resolve(rootDir, value);
}

/**
 * Ensures a target path is inside a root directory
 *
 * @param rootDir - Root directory
 * @param targetPath - Target path to check
 * @throws Error if targetPath escapes rootDir
 */
export function ensureInsideRoot(rootDir: string, targetPath: string): void {
  const resolvedRoot = resolve(rootDir);
  const resolvedTarget = resolve(targetPath);

  const relativePath = relative(resolvedRoot, resolvedTarget);

  // Check if relative path starts with '..' or is absolute
  if (relativePath.startsWith('..')) {
    throw new Error(`Target path "${targetPath}" escapes root directory "${rootDir}"`);
  }
}

/**
 * Gets the relative path from root directory to target path
 *
 * @param rootDir - Root directory
 * @param targetPath - Target path
 * @returns Relative path in POSIX format
 */
export function getRelativePath(rootDir: string, targetPath: string): string {
  const resolvedRoot = resolve(rootDir);
  const resolvedTarget = resolve(targetPath);

  return toPosixPath(relative(resolvedRoot, resolvedTarget));
}

/**
 * Joins path parts and normalizes to POSIX format
 *
 * @param parts - Path parts to join
 * @returns Joined path in POSIX format
 */
export function joinPath(...parts: string[]): string {
  return toPosixPath(join(...parts));
}

/**
 * Gets the directory name of a file path
 *
 * @param filePath - File path
 * @returns Directory name
 */
export function dirnameOf(filePath: string): string {
  return dirname(filePath);
}

/**
 * Gets the base name of a file path
 *
 * @param filePath - File path
 * @returns Base name
 */
export function basenameOf(filePath: string): string {
  return basename(filePath);
}

/**
 * Removes the extension from a file path
 *
 * @param filePath - File path
 * @returns File path without extension
 */
export function removeExtension(filePath: string): string {
  const ext = extname(filePath);
  return filePath.slice(0, -ext.length);
}

/**
 * Checks if a file path has one of the specified extensions
 *
 * @param filePath - File path to check
 * @param extensions - Array of extensions to check (with or without leading dot)
 * @returns True if file has one of the extensions
 */
export function hasExtension(filePath: string, extensions: string[]): boolean {
  const ext = extname(filePath).toLowerCase();
  const normalizedExtensions = extensions.map((e) => (e.toLowerCase().startsWith('.') ? e : `.${e}`));

  return normalizedExtensions.includes(ext);
}
