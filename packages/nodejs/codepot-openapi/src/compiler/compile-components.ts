import type { OpenApiComponents } from '../openapi/openapi.types.js';
import type { VersionContract } from '../version/version-contract.types.js';
import type { CompilerContext } from './compiler-context.js';

import type { PropertyRefGroup } from '../properties/property.types.js';
import type { SchemaFieldMap } from '../schema/schema.types.js';

import { toSchemaName } from '../naming/schema-name.js';
import { buildSchemaResolver } from './schemas/build-schema-resolver.js';
import { compileComponentSchema } from './schemas/compile-component-schema.js';
import { compileNamedPropertySchema } from './schemas/compile-named-property-schema.js';
import { compilePropertyGroupSchema } from './schemas/compile-property-group-schema.js';
import { compileParameterComponent } from './components/compile-parameter-component.js';
import { compileRequestBodyComponent } from './components/compile-request-body-component.js';
import { compileResponseComponent } from './components/compile-response-component.js';
import { resolvePendingRefs } from './refs/resolve-pending-refs.js';

type SchemaResolver = ReturnType<typeof buildSchemaResolver>;

export interface CompiledComponentsResult {
  readonly components: OpenApiComponents;
  readonly resolver: SchemaResolver;
}

export function compileComponents(contract: VersionContract, context: CompilerContext): CompiledComponentsResult {
  const resolver = buildSchemaResolver(
    contract.resources,
    contract.properties,
    contract.schemaComponents,
    contract.parameterComponents,
    contract.requestBodyComponents,
    contract.responseComponents,
    contract.frontends,
    context,
  );

  const schemas: Record<string, unknown> = {};
  const parameters: Record<string, unknown> = {};
  const requestBodies: Record<string, unknown> = {};
  const responses: Record<string, unknown> = {};

  emitPropertyComponents(contract.properties, schemas, resolver, context);
  emitRootSchemaComponents(contract, schemas, resolver, context);
  emitRootParameterComponents(contract, parameters, resolver);
  emitRootRequestBodies(contract, requestBodies, resolver);
  emitRootResponses(contract, responses, resolver);

  for (const resource of contract.resources) {
    emitPropertyComponents(resource.properties, schemas, resolver, context);
    emitResourceSchemaComponents(resource.schemaComponents, schemas, resolver, context);
    emitResourceParameterComponents(resource.parameterComponents, parameters, resolver);
    emitResourceRequestBodies(resource.requestBodyComponents, requestBodies, resolver);
    emitResourceResponses(resource.responseComponents, responses, resolver);
  }

  for (const frontend of contract.frontends) {
    emitResourceSchemaComponents(frontend.schemaComponents, schemas, resolver, context);
  }

  return {
    components: {
      schemas,
      parameters,
      requestBodies,
      responses,
    },
    resolver,
  };
}

/* =========================================================
 * Root-level component emission
 * ========================================================= */

function emitRootSchemaComponents(
  contract: VersionContract,
  schemas: Record<string, unknown>,
  resolver: SchemaResolver,
  context: CompilerContext,
): void {
  for (const registry of contract.schemaComponents) {
    for (const definition of registry.definitions) {
      const ref = registry.ref[definition.name];
      const name = resolver.schemas.get(ref.id) ?? definition.name;

      schemas[name] = resolvePendingRefs(compileComponentSchema(definition, ref, context), resolver, context);
    }
  }
}

function emitRootParameterComponents(contract: VersionContract, parameters: Record<string, unknown>, resolver: SchemaResolver): void {
  for (const registry of contract.parameterComponents) {
    for (const definition of registry.definitions) {
      const name = resolver.parameters.get(registry.ref[definition.key].id);
      if (!name) continue;

      parameters[name] = compileParameterComponent(definition, resolver);
    }
  }
}

function emitRootRequestBodies(contract: VersionContract, requestBodies: Record<string, unknown>, resolver: SchemaResolver): void {
  for (const registry of contract.requestBodyComponents) {
    for (const definition of registry.definitions) {
      const name = resolver.requestBodies.get(registry.ref[definition.name].id);
      if (!name) continue;

      requestBodies[name] = compileRequestBodyComponent(definition, resolver);
    }
  }
}

function emitRootResponses(contract: VersionContract, responses: Record<string, unknown>, resolver: SchemaResolver): void {
  for (const registry of contract.responseComponents) {
    for (const definition of registry.definitions) {
      const name = resolver.responses.get(registry.ref[definition.name].id);
      if (!name) continue;

      responses[name] = compileResponseComponent(definition, resolver);
    }
  }
}

/* =========================================================
 * Resource-level component emission
 * ========================================================= */

function emitPropertyComponents(
  propertyRegistries: VersionContract['properties'],
  schemas: Record<string, unknown>,
  resolver: SchemaResolver,
  context: CompilerContext,
): void {
  for (const registry of propertyRegistries) {
    for (const definition of registry.definitions) {
      if (!definition.emitSchema) continue;

      const groupRefs = registry.ref[definition.name];

      if (!isPropertyRefGroup(groupRefs)) continue;

      const schemaName = toSchemaName(definition.name);

      schemas[schemaName] = resolvePendingRefs(compilePropertyGroupSchema(definition, groupRefs, resolver), resolver, context);
    }

    for (const value of Object.values(registry.ref)) {
      if (isPropertyRefGroup(value)) {
        emitPropertyGroupNamedSchemas({
          value,
          schemas,
          resolver,
          context,
          definitions: registry.definitions,
        });

        continue;
      }

    }
  }
}

function emitResourceSchemaComponents(
  schemaRegistries: VersionContract['resources'][number]['schemaComponents'],
  schemas: Record<string, unknown>,
  resolver: SchemaResolver,
  context: CompilerContext,
): void {
  for (const registry of schemaRegistries) {
    for (const definition of registry.definitions) {
      const ref = registry.ref[definition.name];
      const name = resolver.schemas.get(ref.id);

      if (!name) continue;

      schemas[name] = resolvePendingRefs(compileComponentSchema(definition, ref, context), resolver, context);
    }
  }
}

function emitResourceParameterComponents(
  parameterRegistries: VersionContract['resources'][number]['parameterComponents'],
  parameters: Record<string, unknown>,
  resolver: SchemaResolver,
): void {
  for (const registry of parameterRegistries) {
    for (const definition of registry.definitions) {
      const name = resolver.parameters.get(registry.ref[definition.key].id);
      if (!name) continue;

      parameters[name] = compileParameterComponent(definition, resolver);
    }
  }
}

function emitResourceRequestBodies(
  requestBodyRegistries: VersionContract['resources'][number]['requestBodyComponents'],
  requestBodies: Record<string, unknown>,
  resolver: SchemaResolver,
): void {
  for (const registry of requestBodyRegistries) {
    for (const definition of registry.definitions) {
      const name = resolver.requestBodies.get(registry.ref[definition.name].id);
      if (!name) continue;

      requestBodies[name] = compileRequestBodyComponent(definition, resolver);
    }
  }
}

function emitResourceResponses(
  responseRegistries: VersionContract['resources'][number]['responseComponents'],
  responses: Record<string, unknown>,
  resolver: SchemaResolver,
): void {
  for (const registry of responseRegistries) {
    for (const definition of registry.definitions) {
      const name = resolver.responses.get(registry.ref[definition.name].id);
      if (!name) continue;

      responses[name] = compileResponseComponent(definition, resolver);
    }
  }
}

/* =========================================================
 * Property and entity schema emission
 * ========================================================= */

function emitPropertyGroupNamedSchemas(input: {
  readonly value: PropertyRefGroup;
  readonly schemas: Record<string, unknown>;
  readonly resolver: SchemaResolver;
  readonly context: CompilerContext;
  readonly definitions: readonly { readonly fields: unknown }[];
}): void {
  const { value, schemas, resolver, context, definitions } = input;

  for (const [key, fieldRef] of Object.entries(value)) {
    // Extract underlying ref if it's a RefUsage
    const ref = 'ref' in fieldRef ? fieldRef.ref : fieldRef;

    if (ref.targetRefId) continue;

    const name = resolver.schemas.get(ref.id);

    const definition = definitions.find((item) => {
      return key in (item.fields as Record<string, unknown>);
    });

    const sourceField = (definition?.fields as Record<string, unknown>)?.[key] as SchemaFieldMap[string] | undefined;

    if (!name || !sourceField) continue;

    schemas[name] = resolvePendingRefs(compileNamedPropertySchema(sourceField, ref, context), resolver, context);
  }
}

/* =========================================================
 * Guards
 * ========================================================= */

function isPropertyRefGroup(value: unknown): value is PropertyRefGroup {
  return (
    !!value &&
    typeof value === 'object' &&
    !Array.isArray(value) &&
    !('model' in value)
  );
}
