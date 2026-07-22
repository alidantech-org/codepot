import { dirname, resolve, relative } from 'node:path';

export function toPosixPath(path: string): string {
  return path.replace(/\\/g, '/');
}

export function resolveInsideRoot(rootDir: string, filePath: string): string {
  const absolutePath = resolve(rootDir, filePath);
  ensureInsideRoot(rootDir, absolutePath);
  return absolutePath;
}

export function ensureInsideRoot(rootDir: string, absolutePath: string): void {
  const root = resolve(rootDir);
  const target = resolve(absolutePath);

  // Normalize paths to use forward slashes for comparison
  const normalizedRoot = toPosixPath(root);
  const normalizedTarget = toPosixPath(target);

  if (normalizedTarget !== normalizedRoot && !normalizedTarget.startsWith(normalizedRoot + '/')) {
    throw new Error(`File path escapes root directory: ${absolutePath}`);
  }
}

export function relativeFromRoot(rootDir: string, absolutePath: string): string {
  return toPosixPath(relative(rootDir, absolutePath));
}

export function parentDir(filePath: string): string {
  return dirname(filePath);
}
