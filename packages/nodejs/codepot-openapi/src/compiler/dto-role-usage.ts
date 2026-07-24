import { XCodegenDtoRole } from '../codegen/codegen-extension.types.js';
import type { VersionContract } from '../version/version-contract.types.js';
import type { CompilerContext } from './compiler-context.js';
import { isComponentRef, isPropertyRef } from '../validation/ref-guards.js';
import { isRefUsage } from '../validation/ref-usage-guards.js';

/**
 * Collects DTO role usage from all routes in the contract.
 * This is a prepass that runs before component compilation.
 */
export function collectDtoRoleUsageFromContract(contract: VersionContract, context: CompilerContext): void {
  if (!context.dtoRoleUsage) return;

  for (const resource of contract.resources) {
    for (const routeRegistry of resource.routeRegistries) {
      recordDtoRoleUsage(routeRegistry.params, XCodegenDtoRole.params, context.dtoRoleUsage);

      for (const route of Object.values(routeRegistry.routes)) {
        collectDtoRoleUsageFromRoute(route, context);
      }
    }
  }
}

function collectDtoRoleUsageFromRoute(route: unknown, context: CompilerContext): void {
  if (!route || typeof route !== 'object') return;

  const routeObj = route as Record<string, unknown>;
  const usage = context.dtoRoleUsage;
  if (!usage) return;

  recordDtoRoleUsage(routeObj.query, XCodegenDtoRole.query, usage);
  recordDtoRoleUsage(routeObj.body, XCodegenDtoRole.body, usage);
  recordDtoRoleUsage(routeObj.response, XCodegenDtoRole.response, usage);

  // Handle responses object
  if (routeObj.responses && typeof routeObj.responses === 'object') {
    for (const response of Object.values(routeObj.responses)) {
      recordDtoRoleUsage(response, XCodegenDtoRole.response, usage);
    }
  }
}

/**
 * Records DTO role usage for a given value.
 * Only records ComponentRef DTOs, not PropertyRef or ModelRef.
 */
export function recordDtoRoleUsage(value: unknown, role: XCodegenDtoRole, usage: Map<string, Set<XCodegenDtoRole>>): void {
  if (!value) return;

  // Handle RefUsage - unwrap and record
  if (isRefUsage(value)) {
    recordDtoRoleUsage(value.ref, role, usage);
    recordDtoRoleUsage(value.usage.extendWith, role, usage);
    return;
  }

  // Handle ComponentRef - record role
  if (isComponentRef(value)) {
    addDtoRole(usage, value.id, role);
    return;
  }

  // Skip PropertyRef and ModelRef - they are not DTO components
  if (isPropertyRef(value)) return;
  if (typeof value === 'object' && value !== null && 'kind' in value && (value as { kind: string }).kind === 'model') return;

  // Handle objects with schema property (response/body wrappers)
  if (typeof value === 'object' && !Array.isArray(value)) {
    if ('schema' in value) {
      recordDtoRoleUsage((value as { schema: unknown }).schema, role, usage);
      return;
    }

    // Recurse into object values
    for (const child of Object.values(value)) {
      recordDtoRoleUsage(child, role, usage);
    }
  }

  // Handle arrays - recurse
  if (Array.isArray(value)) {
    for (const item of value) {
      recordDtoRoleUsage(item, role, usage);
    }
  }
}

function addDtoRole(usage: Map<string, Set<XCodegenDtoRole>>, refId: string, role: XCodegenDtoRole): void {
  const existing = usage.get(refId) ?? new Set();
  existing.add(role);
  usage.set(refId, existing);
}
