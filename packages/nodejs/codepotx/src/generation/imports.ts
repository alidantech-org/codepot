import {
  normalizePortablePath,
  portableDirname,
  portableRelative,
} from '@/internal/paths/portable-path';

import type {
  GenerationImportAdapter,
  GenerationImportRequest,
  GenerationImportResult,
} from './imports.types';

/**
 * Framework-neutral import adapter. Language packs may inject a richer adapter
 * that adds file extensions, package aliases, symbols, or language statements.
 */
export class RelativeImportAdapter implements GenerationImportAdapter {
  readonly id = 'relative';

  resolve(request: GenerationImportRequest): GenerationImportResult {
    const fromDirectory = portableDirname(normalizePath(request.fromPath));
    const target = stripKnownSourceExtension(normalizePath(request.toPath));
    const value = portableRelative(fromDirectory, target);
    const importPath = value.startsWith('.') ? value : `./${value}`;
    return { importPath };
  }
}

export function createRelativeImportAdapter(): GenerationImportAdapter {
  return new RelativeImportAdapter();
}

function normalizePath(path: string): string {
  const normalized = normalizePortablePath(path);
  return normalized.startsWith('./') ? normalized.slice(2) : normalized;
}

function stripKnownSourceExtension(path: string): string {
  return path.replace(/\.(?:d\.)?(?:[cm]?[jt]sx?|dart|py|java|kt|go|rs)$/i, '');
}
