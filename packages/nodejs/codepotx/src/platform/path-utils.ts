import { isAbsolute, normalize, relative, resolve, sep } from 'node:path';

import type { PortablePath } from '@/contract/index';

export function normalizePath(path: PortablePath, cwd: PortablePath = process.cwd()): PortablePath {
  return normalize(isAbsolute(path) ? path : resolve(cwd, path));
}

export function isPathWithin(path: PortablePath, root: PortablePath): boolean {
  const normalizedPath = normalizePath(path);
  const normalizedRoot = normalizePath(root);
  const relation = relative(normalizedRoot, normalizedPath);
  return relation === '' || (!relation.startsWith(`..${sep}`) && relation !== '..' && !isAbsolute(relation));
}

export function assertPathWithin(path: PortablePath, root: PortablePath): void {
  if (!isPathWithin(path, root)) {
    throw new Error(`Path escapes the allowed root: ${path}`);
  }
}

export function toPosixPath(path: PortablePath): PortablePath {
  return path.split(sep).join('/');
}

export function globPatternToRegExp(pattern: string): RegExp {
  let expression = '^';
  let index = 0;

  while (index < pattern.length) {
    const current = pattern[index];
    const next = pattern[index + 1];

    if (current === '*' && next === '*') {
      const after = pattern[index + 2];
      expression += after === '/' ? '(?:.*/)?' : '.*';
      index += after === '/' ? 3 : 2;
      continue;
    }

    if (current === '*') {
      expression += '[^/]*';
      index += 1;
      continue;
    }

    if (current === '?') {
      expression += '[^/]';
      index += 1;
      continue;
    }

    if (current === '[') {
      const close = pattern.indexOf(']', index + 1);
      if (close !== -1) {
        expression += pattern.slice(index, close + 1);
        index = close + 1;
        continue;
      }
    }

    expression += current?.replace(/[\\^$+?.()|{}]/g, '\\$&') ?? '';
    index += 1;
  }

  return new RegExp(`${expression}$`);
}

export function matchesAnyGlob(path: string, patterns: readonly string[]): boolean {
  return patterns.some((pattern) => globPatternToRegExp(pattern.replaceAll('\\', '/')).test(path.replaceAll('\\', '/')));
}
