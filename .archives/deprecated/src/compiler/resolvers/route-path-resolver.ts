// src/compiler/resolvers/route-path-resolver.ts

// ============================================================================
// PATH JOINING
// ============================================================================

/**
 * Normalizes one path segment.
 */
function trimSlashes(value: string): string {
  return value.replace(/^\/+|\/+$/g, '');
}

/**
 * Joins resource base path and route path into one absolute route path.
 *
 * Examples:
 * /users + /     -> /users
 * /users + /:id  -> /users/:id
 * users  + :id   -> /users/:id
 */
export function joinRoutePath(basePath: string, routePath: string): string {
  const base = trimSlashes(basePath);
  const route = trimSlashes(routePath);

  if (base.length === 0 && route.length === 0) return '/';
  if (route.length === 0) return `/${base}`;
  if (base.length === 0) return `/${route}`;

  return `/${base}/${route}`;
}

// ============================================================================
// PATH PARAMETERS
// ============================================================================

/**
 * Extracts colon path params from a route path.
 *
 * Example:
 * /users/:id/posts/:postId -> ["id", "postId"]
 */
export function extractPathParameterNames(path: string): readonly string[] {
  const matches = path.matchAll(/:([A-Za-z_][A-Za-z0-9_]*)/g);

  return [...matches].map((match) => match[1]);
}
