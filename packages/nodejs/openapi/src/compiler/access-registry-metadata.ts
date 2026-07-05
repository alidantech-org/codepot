import type { AccessRef, NormalizedAccessDefinition } from '../access/access.types.js';
import type { VersionContract } from '../version/version-contract.types.js';
import type { RefResolver } from './refs/ref-resolver.types.js';

export type ResolvedAccessRegistryMetadata = {
  readonly access?: {
    readonly global?: Record<string, unknown>;
  };
  readonly resourceAccess: Record<string, Record<string, unknown>>;
  readonly policies: Map<string, Record<string, unknown>>;
};

export function compileAccessRegistryMetadata(contract: VersionContract, resolver: RefResolver): ResolvedAccessRegistryMetadata {
  const global: Record<string, unknown> = {};
  const resources: Record<string, Record<string, unknown>> = {};
  const policies = new Map<string, Record<string, unknown>>();

  for (const registry of contract.accessComponents) {
    for (const definition of registry.definitions) {
      const policy = resolveAccessPolicy(definition, resolver);
      global[definition.key] = policy;
      policies.set(accessPolicyId(definition.owner, definition.key), policy);
    }
  }

  for (const resource of contract.resources) {
    for (const registry of resource.accessComponents) {
      if (!('resource' in registry.owner)) continue;
      const resourceName = registry.owner.resource.name;
      const target = (resources[resourceName] ??= {});

      for (const definition of registry.definitions) {
        const policy = resolveAccessPolicy(definition, resolver);
        target[definition.key] = policy;
        policies.set(accessPolicyId(definition.owner, definition.key), policy);
      }
    }
  }

  return {
    access: cleanObject({
      global: Object.keys(global).length > 0 ? global : undefined,
    }) as ResolvedAccessRegistryMetadata['access'],
    resourceAccess: resources,
    policies,
  };
}

export function compactOperationAccess(access: AccessRef | undefined, resolver: RefResolver, policies: ReadonlyMap<string, Record<string, unknown>>): Record<string, unknown> | undefined {
  if (!access) return undefined;

  const policyId = accessPolicyId(access.owner, access.key);
  const rootPolicy = policies.get(policyId);
  const operationPolicy = resolveAccessPolicy(access.definition, resolver);

  if (!rootPolicy) {
    throw new Error(`Operation access "${policyId}" does not match any root access registry definition.`);
  }

  if (!deepEqual(rootPolicy, operationPolicy)) {
    throw new Error(`Operation access "${policyId}" does not match the root access registry definition.`);
  }

  return {
    $ref: accessPolicyRef(access.owner, access.key),
  };
}

export function accessPolicyRef(owner: AccessRef['owner'], key: string): string {
  if ('global' in owner) return `#/x-codegen/access/global/${key}`;
  return `#/x-codegen/resources/${owner.resource.name}/access/${key}`;
}

function resolveAccessPolicy(definition: NormalizedAccessDefinition, resolver: RefResolver): Record<string, unknown> {
  return cleanObject({
    context: resolveAccessContext(definition, resolver),
    roles: resolveAccessRoles(definition, resolver),
    tags: definition.tags,
    description: definition.description,
    info: definition.info,
  });
}

function resolveAccessContext(access: Pick<NormalizedAccessDefinition, 'context'>, resolver: RefResolver): unknown {
  const context = access.context;

  if (context === null) return null;

  const schemaName = resolver.schemas.get(context.id) ?? context.name;
  return { $ref: `#/components/schemas/${schemaName}` };
}

function resolveAccessRoles(access: Pick<NormalizedAccessDefinition, 'roles'>, resolver: RefResolver): Record<string, unknown> | undefined {
  const roles = access.roles;
  if (!roles) return undefined;

  return Object.fromEntries(
    Object.entries(roles).map(([realm, role]) => [
      realm,
      cleanObject({
        source: resolveAccessRoleSource(role.source, resolver),
        allow: role.allow,
      }),
    ]),
  );
}

function resolveAccessRoleSource(source: { readonly id: string; readonly name: string }, resolver: RefResolver): unknown {
  const schemaName = resolver.schemas.get(source.id) ?? source.name;
  return { $ref: `#/components/schemas/${schemaName}` };
}

function accessPolicyId(owner: AccessRef['owner'], key: string): string {
  if ('global' in owner) return `global.${key}`;
  return `${owner.resource.name}.${key}`;
}

function deepEqual(left: unknown, right: unknown): boolean {
  return JSON.stringify(sortValue(left)) === JSON.stringify(sortValue(right));
}

function sortValue(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(sortValue);

  if (value && typeof value === 'object') {
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>)
        .sort(([left], [right]) => left.localeCompare(right))
        .map(([key, child]) => [key, sortValue(child)]),
    );
  }

  return value;
}

function cleanObject(input: Record<string, unknown>): Record<string, unknown> {
  return Object.fromEntries(Object.entries(input).filter(([, value]) => value !== undefined));
}
