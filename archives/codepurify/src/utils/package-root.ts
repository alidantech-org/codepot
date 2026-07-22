/**
 * Package Root Finder Utility
 *
 * Helps find the package root directory by walking up the directory tree
 * until it finds a package.json file. This is useful for resolving
 * built-in template paths from within the installed package.
 */

import { access, constants } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';

/**
 * Finds the package root directory by walking up from a starting directory
 *
 * @param startDir - Directory to start searching from
 * @returns Promise resolving to the package root directory path
 * @throws Error if package.json is not found
 */
export async function findPackageRoot(startDir: string): Promise<string> {
  let currentDir = resolve(startDir);

  while (true) {
    const packageJsonPath = resolve(currentDir, 'package.json');

    try {
      await access(packageJsonPath, constants.F_OK);

      // Verify this is the codepurify package
      const { readFile } = await import('node:fs/promises');
      const packageJson = JSON.parse(await readFile(packageJsonPath, 'utf-8'));

      if (packageJson.name === 'codepurify') {
        return currentDir;
      }
    } catch {
      // Continue searching if not codepurify package or file not found
    }

    // package.json not found or not codepurify package, go up one level
    const parentDir = dirname(currentDir);

    // If we've reached the root directory and still haven't found package.json
    if (parentDir === currentDir) {
      throw new Error('codepurify package.json not found in directory tree');
    }

    currentDir = parentDir;
  }
}

/**
 * Gets the package root directory from the current module's location
 *
 * @param importMetaUrl - import.meta.url from the calling module
 * @returns Promise resolving to the package root directory path
 */
export async function getPackageRootFromModule(importMetaUrl: string): Promise<string> {
  const { fileURLToPath } = await import('node:url');
  const { dirname } = await import('node:path');

  const currentFile = fileURLToPath(importMetaUrl);
  const currentDir = dirname(currentFile);

  return findPackageRoot(currentDir);
}
