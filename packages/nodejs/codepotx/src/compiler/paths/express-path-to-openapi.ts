export function expressPathToOpenApi(path: string): string {
  return normalizeOpenApiPath(path).replace(/:(\w+)/g, '{$1}');
}

export function normalizeOpenApiPath(path: string): string {
  const normalized = path.replace(/\\/g, '/').replace(/\/+/g, '/').replace(/^\/?/, '/');

  if (normalized === '/') {
    return '/';
  }

  return normalized.replace(/\/$/, '');
}
