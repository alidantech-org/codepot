import type { SchemaComponentRegistry } from '../../components/schemas/schema-component.types.js';
import type { ParameterComponentRegistry } from '../../components/parameters/parameter-component.types.js';
import type { RequestBodyComponentRegistry } from '../../components/request-bodies/request-body-component.types.js';
import type { ResponseComponentRegistry } from '../../components/responses/response-component.types.js';
import type { CompilerContext } from '../compiler-context.js';
import { componentRefToSchemaName } from '../../naming/ref-schema-name.js';
import type { PropertyRefGroup, PropertyRegistry, PropertyRegistryRef } from '../../properties/property.types.js';
import type { PropertyRef } from '../../refs/ref.types.js';
import type { ResourceBuilder } from '../../resource/define-resource.js';
import type { FrontendBuilder } from '../../frontend/frontend.types.js';
import type { RefResolver } from '../refs/ref-resolver.types.js';
import { toSchemaName } from '../../naming/schema-name.js';

export function buildSchemaResolver(
  resources: readonly ResourceBuilder[],
  properties: readonly PropertyRegistry[],
  schemaComponents: readonly SchemaComponentRegistry[],
  parameterComponents: readonly ParameterComponentRegistry[],
  requestBodyComponents: readonly RequestBodyComponentRegistry[],
  responseComponents: readonly ResponseComponentRegistry[],
  frontends: readonly FrontendBuilder[] = [],
  context?: CompilerContext,
): RefResolver {
  const schemas = new Map<string, string>();
  const parameters = new Map<string, string>();
  const requestBodies = new Map<string, string>();
  const responses = new Map<string, string>();

  for (const registry of properties) {
    registerPropertyRegistry(registry, schemas);
  }

  for (const registry of schemaComponents) {
    registerComponentRegistry(registry, schemas);
  }

  for (const registry of parameterComponents) {
    registerRefRegistry(registry.ref, parameters);
  }

  for (const registry of requestBodyComponents) {
    registerRefRegistry(registry.ref, requestBodies);
  }

  for (const registry of responseComponents) {
    registerRefRegistry(registry.ref, responses);
  }

  for (const resource of resources) {
    for (const registry of resource.properties) {
      registerPropertyRegistry(registry, schemas);
    }

    for (const registry of resource.schemaComponents) {
      registerComponentRegistry(registry, schemas);
    }

    for (const registry of resource.parameterComponents) {
      registerRefRegistry(registry.ref, parameters);
    }

    for (const registry of resource.requestBodyComponents) {
      registerRefRegistry(registry.ref, requestBodies);
    }

    for (const registry of resource.responseComponents) {
      registerRefRegistry(registry.ref, responses);
    }
  }

  for (const frontend of frontends) {
    for (const registry of frontend.schemaComponents) {
      registerComponentRegistry(registry, schemas);
    }
  }

  return {
    schemas,
    parameters,
    requestBodies,
    responses,
  };
}

function registerComponentRegistry(registry: SchemaComponentRegistry, schemas: Map<string, string>): void {
  for (const ref of Object.values(registry.ref)) {
    schemas.set(ref.id, componentRefToSchemaName(ref));
  }
}

function registerPropertyRegistry(registry: PropertyRegistry, schemas: Map<string, string>): void {
  for (const [groupName, value] of Object.entries(registry.ref)) {
    const definition = registry.definitions.find((item) => {
      return item.name === groupName;
    });

    registerPropertyRegistryRef(groupName, value, schemas, definition);
  }
}

function registerPropertyRegistryRef(
  groupName: string,
  value: PropertyRegistryRef,
  schemas: Map<string, string>,
  definition: PropertyRegistry['definitions'][number] | undefined,
): void {
  if (definition?.emitSchema && isPropertyRefGroup(value)) {
    schemas.set(toSchemaName(groupName), toSchemaName(groupName));
  }

  if (isPropertyRefGroup(value)) {
    registerPropertyGroupRefs(groupName, value, schemas);
  }
}

function registerPropertyGroupRefs(groupName: string, value: PropertyRefGroup, schemas: Map<string, string>): void {
  for (const [key, fieldRef] of Object.entries(value)) {
    // Extract underlying ref if it's a RefUsage
    const ref = 'ref' in fieldRef ? fieldRef.ref : fieldRef;

    if (registerAliasRef(ref, schemas)) continue;

    schemas.set(ref.id, toSchemaName(groupName, key));
  }
}

function registerRefRegistry(refs: Record<string, { id: string; name: string }>, target: Map<string, string>): void {
  for (const ref of Object.values(refs)) {
    target.set(ref.id, ref.name);
  }
}

function isPropertyRefGroup(value: PropertyRegistryRef): value is PropertyRefGroup {
  return !!value && typeof value === 'object' && !Array.isArray(value) && !('model' in value);
}

function registerAliasRef(ref: PropertyRef, schemas: Map<string, string>): boolean {
  if (!ref.targetRefId) return false;

  const targetName = schemas.get(ref.targetRefId);

  if (!targetName) return false;

  schemas.set(ref.id, targetName);
  return true;
}
