import { dirname, relative } from 'node:path/posix';

import type { GenerationImportAdapter, GenerationImportRequest, GenerationImportResult } from './imports.types';

/**
 * Framework-neutral import adapter. Language packs may inject a richer adapter
 * that adds file extensions, package aliases, symbols, or language statements.
 */
export class RelativeImportAdapter implements GenerationImportAdapter {
  readonly id = 'relative';

  resolve(request: GenerationImportRequest): GenerationImportResult {
    const fromDirectory = dirname(normalizePath(request.fromPath));
    const target = stripKnownSourceExtension(normalizePath(request.toPath));
    const value = relative(fromDirectory, target);
    const importPath = value.startsWith('.') ? value : `./${value}`;
    return { importPath };
  }
}

export function createRelativeImportAdapter(): GenerationImportAdapter {
  return new RelativeImportAdapter();
}

function normalizePath(path: string): string {
  return path.replaceAll('\\', '/').replace(/^\.\//, '');
}

function stripKnownSourceExtension(path: string): string {
  return path.replace(/\.(?:d\.)?(?:[cm]?[jt]sx?|dart|py|java|kt|go|rs)$/i, '');
}
