// src/compiler/passes/08-resources.ts

import type { ResourceAuthoringState } from '@/contract/types/authoring/6.resource-builder';

import type { ResourceDefinition } from '@/contract/types/ir/resource/definition';
import type { RouteMethodDefinition } from '@/contract/types/ir/resource/route/definition';
import type { RoutesDefinition } from '@/contract/types/ir/resource/route/definition';

import type { CompilerContext } from '../context/compiler-context';

import { resolveRoute } from '../resolvers/route-resolver';
import { extractPathParameterNames, joinRoutePath } from '../resolvers/route-path-resolver';

import { securityPolicyRef } from '../resolvers/ref-resolver';

import { toSnakeCaseKey } from '@/utils/naming/normalize-key';

type MutableRoutePathDefinition = {
  path: RoutesDefinition[string]['path'];
  parameters?: NonNullable<RoutesDefinition[string]['parameters']>;
  methods: RoutesDefinition[string]['methods'];
};

// ============================================================================
// RESOURCE DEFAULTS
// ============================================================================

/**
 * Resolves resource default security into an IR security policy ref.
 */
function resolveResourceDefaultSecurity(
  security: ResourceAuthoringState['defaults']['security'],
): ResourceDefinition['defaults']['security'] {
  if (security === undefined) return undefined;

  if (typeof security === 'object' && 'key' in security && typeof security.key === 'string') {
    return securityPolicyRef(toSnakeCaseKey(security.key));
  }

  return undefined;
}

// ============================================================================
// ROUTES
// ============================================================================

/**
 * Returns the resource base path.
 *
 * If no explicit base path exists, use /resource_key.
 */
function resolveResourceBasePath(resourceKey: string, resource: ResourceAuthoringState): string {
  const resourceWithPath = resource as ResourceAuthoringState & {
    readonly basePath?: string;
    readonly base_path?: string;
  };

  return resourceWithPath.basePath ?? resourceWithPath.base_path ?? `/${resourceKey}`;
}

/**
 * Resolves path-level params for a full route path.
 */
function resolvePathLevelParameters(fullPath: string, method: RouteMethodDefinition): NonNullable<RoutesDefinition[string]['parameters']> {
  const names = extractPathParameterNames(fullPath);

  if (names.length === 0) return {};
  if (method.params === undefined) return {};

  const params = method.params;

  return Object.fromEntries(names.map((name) => [name, params]));
}

/**
 * Creates a route path map grouped by URL path and HTTP method.
 */
function resolveResourceRoutes(
  ctx: CompilerContext,
  resourceKey: string,
  resource: ResourceAuthoringState,
): {
  readonly operations: ResourceDefinition['operations'];
  readonly routes: RoutesDefinition;
} {
  const operations: ResourceDefinition['operations'] = {};
  const routes: RoutesDefinition = {};
  const basePath = resolveResourceBasePath(resourceKey, resource);

  for (const [routeKey, route] of Object.entries(resource.routes ?? {})) {
    const resolved = resolveRoute({
      ctx,
      resourceKey,
      routeKey,
      route,
    });

    operations[resolved.operationKey] = resolved.operation;

    const fullPath = joinRoutePath(basePath, route.path);
    const pathParameters = resolvePathLevelParameters(fullPath, resolved.method);

    routes[fullPath] ??= {
      path: fullPath,
      methods: {},
    };

    const routePath = routes[fullPath] as MutableRoutePathDefinition;

    routePath.methods[route.method] = resolved.method;

    if (Object.keys(pathParameters).length > 0) {
      routePath.parameters = {
        ...(routePath.parameters ?? {}),
        ...pathParameters,
      };
    }
  }

  return {
    operations,
    routes,
  };
}

// ============================================================================
// RESOURCE
// ============================================================================

/**
 * Compiles one authoring resource into an IR resource.
 */
function resolveResource(ctx: CompilerContext, key: string, resource: ResourceAuthoringState): ResourceDefinition {
  const compiledKey = toSnakeCaseKey(key);
  const resolvedRoutes = resolveResourceRoutes(ctx, compiledKey, resource);
  const basePath = resolveResourceBasePath(compiledKey, resource);

  return {
    ...(resource.description !== undefined ? { description: resource.description } : {}),
    ...(resource.deprecated !== undefined ? { deprecated: resource.deprecated } : {}),
    ...(resource.meta !== undefined ? { meta: resource.meta } : {}),

    base_path: basePath,
    folders: [...resource.folders],

    defaults: {
      ...(resource.defaults.security !== undefined ? { security: resolveResourceDefaultSecurity(resource.defaults.security) } : {}),
    },

    operations: resolvedRoutes.operations,
    routes: resolvedRoutes.routes,
  };
}

// ============================================================================
// PASS
// ============================================================================

/**
 * Compiles authoring resources into IR resources.
 *
 * Operations are created here from routes. Authoring does not own operations.
 */
export function compileResources(ctx: CompilerContext): void {
  for (const [key, resource] of Object.entries(ctx.authoring.resources ?? {})) {
    ctx.ir.resources[toSnakeCaseKey(key)] = resolveResource(ctx, key, resource);
  }
}
