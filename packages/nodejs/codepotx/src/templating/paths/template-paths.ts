export function joinTemplatePath(root: string, path: string): string {
  return `${root.replace(/[\\/]$/, '')}/${path.replace(/^[\\/]/, '')}`;
}

export function relativeTemplatePath(root: string, path: string): string {
  return path
    .replaceAll('\\', '/')
    .replace(`${root.replaceAll('\\', '/').replace(/\/$/, '')}/`, '');
}

export function isPartialPath(
  path: string,
  configured: readonly string[],
): boolean {
  const normalized = path.replaceAll('\\', '/');
  return normalized.startsWith('_partials/')
    || normalized.includes('/_partials/')
    || normalized.startsWith('partials/')
    || normalized.includes('/partials/')
    || configured.some((pattern) => matchesTemplateGlob(normalized, pattern));
}

export function partialNameFor(path: string, extension: string): string {
  const withoutExtension = path.endsWith(extension)
    ? path.slice(0, -extension.length)
    : path;
  const segments = withoutExtension.split('/');
  const marker = Math.max(
    segments.lastIndexOf('_partials'),
    segments.lastIndexOf('partials'),
  );
  return (marker >= 0 ? segments.slice(marker + 1) : segments)
    .join('/')
    .replace(/^\{[^}]+\}\//, '');
}

export function matchesTemplateGlob(path: string, pattern: string): boolean {
  const escaped = pattern
    .replace(/[.+^${}()|[\]\\]/g, '\\$&')
    .replaceAll('**', '::DOUBLE_STAR::')
    .replaceAll('*', '[^/]*')
    .replaceAll('::DOUBLE_STAR::', '.*')
    .replaceAll('?', '.');
  return new RegExp(`^${escaped}$`).test(path);
}

export function unsafeTemplatePath(path: string): boolean {
  const normalized = path.replaceAll('\\', '/');
  return normalized.startsWith('/')
    || normalized === '..'
    || normalized.startsWith('../')
    || normalized.includes('/../');
}
