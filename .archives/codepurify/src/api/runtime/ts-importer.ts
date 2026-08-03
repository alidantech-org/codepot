/**
 * TypeScript Importer Utility
 *
 * Handles importing TypeScript modules using jiti runtime transpiler.
 */

import { createJiti } from 'jiti';

// Create a shared jiti instance
const jiti = createJiti(import.meta.url, { interopDefault: true });

/**
 * Imports a TypeScript module using jiti runtime transpiler.
 *
 * @param absolutePath - Absolute path to the TypeScript file
 * @returns Promise resolving to the imported module
 */
export async function importTsModule<T = any>(absolutePath: string): Promise<T> {
  return (await jiti.import(absolutePath)) as T;
}
