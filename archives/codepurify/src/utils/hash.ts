/**
 * Codepurify Hash Utilities
 *
 * Provides cryptographic hashing using Node.js crypto module.
 * Supports content hashing and file hashing with SHA-256.
 */

import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';

/**
 * Error thrown when hashing operations fail
 */
export class HashError extends Error {
  constructor(
    message: string,
    public cause?: Error,
  ) {
    super(message);
    this.name = 'HashError';
  }
}

/**
 * Hashes content using SHA-256
 *
 * @param content - Content to hash (string or Buffer)
 * @returns Hexadecimal hash string
 */
export function hashContent(content: string | Buffer): string {
  try {
    const hash = createHash('sha256');
    hash.update(content);
    return hash.digest('hex');
  } catch (error) {
    throw new HashError('Failed to hash content', error as Error);
  }
}

/**
 * Hashes a file using SHA-256
 *
 * @param filePath - Path to the file to hash
 * @returns Hexadecimal hash string or null if file doesn't exist
 * @throws HashError if file exists but cannot be read
 */
export async function hashFile(filePath: string): Promise<string | null> {
  try {
    const content = await readFile(filePath);
    return hashContent(content);
  } catch (error) {
    const fsError = error as NodeJS.ErrnoException;

    // If file doesn't exist, return null
    if (fsError.code === 'ENOENT') {
      return null;
    }

    // Otherwise, wrap the error
    throw new HashError(`Failed to hash file: ${filePath}`, error as Error);
  }
}

/**
 * Compares two hash values safely
 *
 * @param expected - Expected hash value (can be null/undefined)
 * @param actual - Actual hash value (can be null/undefined)
 * @returns True if hashes match (including both being null/undefined)
 */
export function compareHash(expected: string | null | undefined, actual: string | null | undefined): boolean {
  // Handle null/undefined cases
  if (expected === null || expected === undefined) {
    return actual === null || actual === undefined;
  }

  if (actual === null || actual === undefined) {
    return false;
  }

  // Compare hash strings
  return expected === actual;
}
