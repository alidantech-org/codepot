import type { ComponentFieldMap, SchemaCompositionFieldValue } from '../../components/component.types.js';
import type { SchemaComponentDefinition, SchemaComponentValue } from '../../components/schemas/schema-component.types.js';
import type { ComponentRef, PropertyRef, ModelRef, EngineRef } from '../../refs/ref.types.js';
import type { ArrayRef, ExtendedRef } from '../../refs/ref-wrapper.types.js';
import type { RefUsage } from '../../refs/ref-usage.types.js';
import type { CompilerContext } from '../compiler-context.js';
import { isRefUsage } from '../../validation/ref-usage-guards.js';
import { applyCodegenMetadata } from '../../codegen/apply-codegen-extensions.js';
import { XCodegenKind, XCodegenDtoRole, type CodegenMetadata } from '../../codegen/codegen-extension.types.js';
import { normalizeExtendWithInput, normalizeExtendWithInputWithSource } from './normalize-extend-with.js';

export function compileComponentSchema(
  definition: SchemaComponentDefinition,
  ref?: ComponentRef,
  context?: CompilerContext,
): Record<string, unknown> {
  if (isSchemaProjectionDefinition(definition.value)) {
    throw new Error('Schema projections must be declared as top-level defineSchemas() entries before they are used as fields.');
  }

  // Handle RefUsage with extendWith (allOf)
  if (isRefUsage(definition.value)) {
    return compileExtendedSchemaComponent(definition, ref, context);
  }

  // Handle direct EngineRef (alias)
  if (isEngineRef(definition.value)) {
    const refSchema = { $ref: `#/components/schemas/${definition.value.name}` };
    if (ref?.meta) {
      const enrichedMeta = enrichDtoRoleMetadata(ref.meta, ref.id, context);
      return applyCodegenMetadata(refSchema, enrichedMeta, context);
    }
    return refSchema;
  }

  // Handle ComponentFieldMap (normal object schema)
  const fields = definition.value as ComponentFieldMap;
  const required = definition.required ? [...definition.required] : getRequiredKeys(fields);

  const schema: Record<string, unknown> = {
    type: 'object',
    properties: compileComponentFields(fields),
  };

  if (required.length > 0) {
    schema.required = required;
  }

  const metadata = createSchemaMetadata(definition, ref, context);

  if (metadata && ref) {
    const enrichedMeta = enrichDtoRoleMetadata(metadata, ref.id, context);
    return applyCodegenMetadata(schema, enrichedMeta, context);
  }

  return schema;
}

function compileComponentFields(fields: ComponentFieldMap): Record<string, unknown> {
  return Object.fromEntries(Object.entries(fields).map(([key, value]) => [key, compileCompositionValue(value)]));
}

function compileExtendedSchemaComponent(
  definition: SchemaComponentDefinition,
  ref?: ComponentRef,
  context?: CompilerContext,
): Record<string, unknown> {
  const usage = definition.value as RefUsage<EngineRef>;
  const baseRef = usage.ref as ComponentRef;
  const extendWith = usage.usage.extendWith;

  const allOf: unknown[] = [{ $ref: `#/components/schemas/${baseRef.name}` }];

  const extensionFields = normalizeExtendWithInput(extendWith);

  if (extensionFields) {
    // Query components should not emit required fields (they are always partial)
    const isQueryComponent = definition.name.endsWith('Query');
    const required = isQueryComponent ? [] : getRequiredKeys(extensionFields);

    const extensionSchema: Record<string, unknown> = {
      type: 'object',
      properties: compileComponentFields(extensionFields),
    };

    if (required.length > 0) {
      extensionSchema.required = required;
    }

    allOf.push(extensionSchema);
  }

  const schema: Record<string, unknown> = { allOf };

  const metadata = createSchemaMetadata(definition, ref, context);

  if (metadata && ref) {
    const enrichedMeta = enrichDtoRoleMetadata(metadata, ref.id, context);
    return applyCodegenMetadata(schema, enrichedMeta, context);
  }

  return schema;
}

function createSchemaMetadata(definition: SchemaComponentDefinition, ref?: ComponentRef, context?: CompilerContext): CodegenMetadata | undefined {
  if (!ref?.meta) return undefined;

  return {
    ...ref.meta,
    ...(definition.meta ?? {}),
    ...(context?.accessContextSchemaIds?.has(ref.id) ? { role: XCodegenDtoRole.context } : {}),
    ...(definition.projection ? { projection: definition.projection } : {}),
  } as CodegenMetadata;
}

function isEngineRef(value: unknown): value is EngineRef {
  return !!value && typeof value === 'object' && 'kind' in value && 'id' in value && 'name' in value;
}

function enrichDtoRoleMetadata(metadata: CodegenMetadata, refId: string, context?: CompilerContext): CodegenMetadata {
  // Only enrich DTO metadata
  if (metadata.kind !== XCodegenKind.dto) {
    return metadata;
  }

  // If no context or role usage map, return as-is
  if (!context?.dtoRoleUsage) {
    return metadata;
  }

  const roles = context.dtoRoleUsage.get(refId);

  // If no roles recorded, return as-is
  if (!roles || roles.size === 0) {
    return metadata;
  }

  // If metadata already has a role, don't override (entity helpers have pre-set roles)
  if (metadata.role) {
    return metadata;
  }

  // Convert Set to array
  const rolesArray = Array.from(roles);

  // If single role, use 'role' field
  if (rolesArray.length === 1) {
    return {
      ...metadata,
      role: rolesArray[0],
    };
  }

  // If multiple roles, use 'roles' field
  return {
    ...metadata,
    roles: rolesArray,
  };
}

function compileCompositionValue(value: SchemaCompositionFieldValue): unknown {
  if (isSchemaProjectionDefinition(value)) {
    throw new Error('Schema projections must be declared as top-level defineSchemas() entries before they are used as fields.');
  }

  let ref = isRefUsage(value) ? value.ref : value;
  let array = isRefUsage(value) ? value.usage.array : false;
  const nullable = isRefUsage(value) ? value.usage.nullable : false;
  const source = isRefUsage(value) ? value.usage.source : undefined;
  let extendWith = isRefUsage(value) ? value.usage.extendWith : undefined;

  // Unwrap ArrayRef and ExtendedRef
  if ('kind' in ref) {
    if (ref.kind === 'array-ref') {
      ref = (ref as ArrayRef).ref as unknown as ComponentRef | PropertyRef | ModelRef;
      array = true;
    } else if (ref.kind === 'extended-ref') {
      const extendedRef = ref as ExtendedRef;
      ref = extendedRef.ref as unknown as ComponentRef | PropertyRef | ModelRef;
      extendWith = extendedRef.fields;
    }
  }

  // Ensure ref is a base ref type (PropertyRef, ModelRef, ComponentRef)
  const baseRef = ref as ComponentRef | PropertyRef | ModelRef;
  let schema: unknown = { $ref: `#pending/${baseRef.id}` };

  // Apply extendWith
  if (extendWith) {
    const extensionFields = normalizeExtendWithInput(extendWith);
    if (extensionFields) {
      const extendedProperties = compileComponentFields(extensionFields);
      schema = {
        allOf: [
          schema,
          {
            type: 'object',
            properties: extendedProperties,
          },
        ],
      };
    }
  }

  // Apply array
  if (array) {
    schema = { type: 'array', items: schema };
  }

  // Apply nullable
  if (nullable) {
    const schemaObj = asObject(schema);
    // For OpenAPI 3.1, use type arrays for simple nullable primitives
    if (schemaObj.type && typeof schemaObj.type === 'string') {
      const primitiveTypes = ['string', 'number', 'integer', 'boolean'];
      if (primitiveTypes.includes(schemaObj.type)) {
        const { type, ...rest } = schemaObj;
        schema = {
          ...rest,
          type: [type, 'null'],
        };
      } else {
        schema = {
          anyOf: [schema, { type: 'null' }],
        };
      }
    } else {
      schema = {
        anyOf: [schema, { type: 'null' }],
      };
    }
  }

  if (source) {
    schema = {
      ...asObject(schema),
      'x-codegen': {
        source: normalizeFieldSourceMetadata(source),
      },
    };
  }

  return schema;
}

function normalizeFieldSourceMetadata(source: NonNullable<import('../../refs/ref-usage.types.js').RefUsageOptions['source']>): Record<string, unknown> {
  const sourceRef = source.source ?? source.route.defaultSource;

  if (!sourceRef) {
    throw new Error(`Route "${source.route.name}" has no default source.`);
  }

  return {
    kind: 'route',
    resource: source.route.resource,
    operationId: source.route.routeKey,
    source: sourceRef.name,
    responseField: sourceRef.source.responseField,
    key: sourceRef.source.key,
    label: sourceRef.source.label,
  };
}

function isSchemaProjectionDefinition(value: unknown): boolean {
  return (
    !!value &&
    typeof value === 'object' &&
    !Array.isArray(value) &&
    (value as { kind?: unknown }).kind === 'schema-projection-definition'
  );
}

function asObject(value: unknown): Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    return {};
  }

  return value as Record<string, unknown>;
}

function getRequiredKeys(fields: ComponentFieldMap): string[] {
  return Object.entries(fields)
    .filter(([, value]) => !isOptional(value))
    .map(([key]) => key);
}

function isOptional(value: SchemaCompositionFieldValue): boolean {
  if (!isRefUsage(value)) return false;
  return value.usage.required === false;
}
