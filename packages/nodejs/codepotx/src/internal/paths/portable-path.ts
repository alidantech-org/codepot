export function normalizePortablePath(path: string): string {
  const portable = path.replaceAll('\\', '/');
  const absolute = portable.startsWith('/');
  const segments: string[] = [];

  for (const segment of portable.split('/')) {
    if (!segment || segment === '.') continue;
    if (segment === '..') {
      if (segments.length > 0 && segments.at(-1) !== '..') {
        segments.pop();
      } else if (!absolute) {
        segments.push(segment);
      }
      continue;
    }
    segments.push(segment);
  }

  const value = segments.join('/');
  if (absolute) return value ? `/${value}` : '/';
  return value || '.';
}

export function portableDirname(path: string): string {
  const normalized = normalizePortablePath(path);
  if (normalized === '/') return '/';
  const index = normalized.lastIndexOf('/');
  if (index < 0) return '.';
  if (index === 0) return '/';
  return normalized.slice(0, index);
}

export function portableExtname(path: string): string {
  const normalized = normalizePortablePath(path);
  const name = normalized.slice(normalized.lastIndexOf('/') + 1);
  const index = name.lastIndexOf('.');
  return index <= 0 ? '' : name.slice(index);
}

export function portableRelative(from: string, to: string): string {
  const normalizedFrom = normalizePortablePath(from);
  const normalizedTo = normalizePortablePath(to);
  const fromAbsolute = normalizedFrom.startsWith('/');
  const toAbsolute = normalizedTo.startsWith('/');
  if (fromAbsolute !== toAbsolute) return normalizedTo;

  const fromParts = normalizedFrom.split('/').filter(Boolean);
  const toParts = normalizedTo.split('/').filter(Boolean);
  let common = 0;
  while (
    common < fromParts.length
    && common < toParts.length
    && fromParts[common] === toParts[common]
  ) {
    common += 1;
  }

  return [
    ...fromParts.slice(common).map(() => '..'),
    ...toParts.slice(common),
  ].join('/');
}
