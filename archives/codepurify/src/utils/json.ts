/**
 * Codepurify JSON Utilities
 *
 * Provides JSON file operations with error handling and formatting.
 * Uses Node.js built-in JSON with consistent formatting.
 */

import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';

/**
 * Error thrown when JSON operations fail
 */
export class JsonError extends Error {
  constructor(
    message: string,
    public cause?: Error,
  ) {
    super(message);
    this.name = 'JsonError';
  }
}

/**
 * Reads and parses a JSON file
 *
 * @param filePath - Path to the JSON file
 * @returns Parsed JSON content or null if file doesn't exist
 * @throws JsonError if file exists but cannot be parsed
 */
export async function readJsonFile<T>(filePath: string): Promise<T | null> {
  try {
    const content = await readFile(filePath, 'utf-8');
    return parseJson<T>(content, filePath);
  } catch (error) {
    const fsError = error as NodeJS.ErrnoException;

    // If file doesn't exist, return null
    if (fsError.code === 'ENOENT') {
      return null;
    }

    // Otherwise, wrap the error
    throw new JsonError(`Failed to read JSON file: ${filePath}`, error as Error);
  }
}

/**
 * Writes a value to a JSON file with formatting
 *
 * @param filePath - Path to write to
 * @param value - Value to write
 * @throws JsonError if write operation fails
 */
export async function writeJsonFile(filePath: string, value: unknown): Promise<void> {
  try {
    // Ensure parent directory exists
    await mkdir(dirname(filePath), { recursive: true });

    // Stringify with 2-space indentation and trailing newline
    const content = stringifyJson(value);

    await writeFile(filePath, content, 'utf-8');
  } catch (error) {
    throw new JsonError(`Failed to write JSON file: ${filePath}`, error as Error);
  }
}

/**
 * Parses JSON content with error handling
 *
 * @param content - JSON string to parse
 * @param label - Optional label for error messages
 * @returns Parsed JSON content
 * @throws JsonError if parsing fails
 */
export function parseJson<T>(content: string, label?: string): T {
  try {
    return JSON.parse(content) as T;
  } catch (error) {
    const context = label ? ` in ${label}` : '';
    throw new JsonError(`Failed to parse JSON${context}: ${(error as Error).message}`, error as Error);
  }
}

/**
 * Stringifies a value to JSON with consistent formatting
 *
 * @param value - Value to stringify
 * @returns Formatted JSON string
 */
export function stringifyJson(value: unknown): string {
  return JSON.stringify(value, null, 2) + '\n';
}
