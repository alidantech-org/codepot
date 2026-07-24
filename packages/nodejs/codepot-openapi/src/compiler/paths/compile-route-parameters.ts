import type { ComponentFieldMap } from '../../components/component.types.js';
import type { SchemaComponentValue } from '../../components/schemas/schema-component.types.js';
import type { ModelRef, ComponentRef, PropertyRef } from '../../refs/ref.types.js';
import type { ExtendWithInput, FieldSourceMetadata, RefUsage } from '../../refs/ref-usage.types.js';
import type { RouteParameterRef, RouteParameterMap, RouteParameterFieldValue, RouteQueryInput } from '../../routes/route.types.js';
import type { XCodegenResourceMeta } from '../../codegen/codegen-extension.types.js';
import type { VersionContract } from '../../version/version-contract.types.js';
import type { RefResolver } from '../refs/ref-resolver.types.js';

import { RefKind } from '../../refs/ref-kind.js';
import { getSourceMetadataFromRef } from '../../refs/ref-source-metadata.js';
import { getRefRequired, isRefUsage } from '../../validation/ref-usage-guards.js';
import { isComponentRef, isEngineRef, isPropertyRef } from '../../validation/ref-guards.js';
import { normalizeExtendWithInputWithSource } from '../schemas/normalize-extend-with.js';
import { compileRouteSchema } from './compile-route-schema.js';

export type QueryParameterFieldValue = RouteParameterFieldValue | ModelRef | ComponentRef | RefUsage<ModelRef> | RefUsage<ComponentRef>;

export interface CollectedQueryField {
  readonly name: string;
  readonly field: QueryParameterFieldValue;
  readonly required: boolean;
  readonly source: FieldSourceMetadata;
}

export function compileRouteParameters(
  schema: RouteParameterRef | RouteParameterMap | RouteQueryInput | undefined,
  location: 'path' | 'query',
  resolver: RefResolver,
  contract?: VersionContract,
  useInlineExpansion = false,
): unknown[] {
  if (!schema) return [];

  if (location === 'query' && isComponentRefInput(schema)) {
    if (useInlineExpansion) {
      return compileComponentRefQueryParameters(schema, resolver, contract);
    }

    return [];
  }

  if (isParameterMap(schema)) {
    return Object.entries(schema).map(([name, param]) => ({
      name,
      in: location,
      required: location === 'path' ? true : !isOptional(param),
      schema: compileParameterField(param),
    }));
  }

  if (isComponentFieldMap(schema)) {
    const compiled = compileRouteSchema(schema, resolver);
    const objectSchema = unwrapObjectSchema(compiled);

    if (!objectSchema?.properties) return [];

    return Object.entries(objectSchema.properties).map(([name, property]) => ({
      name,
      in: location,
      required: location === 'path' ? true : isRequired(name, objectSchema.required),
      schema: property,
    }));
  }

  return [];
}

function compileParameterField(param: QueryParameterFieldValue): unknown {
  const ref = isRefUsage(param) ? param.ref : param;
  const nullable = isRefUsage(param) ? param.usage.nullable : undefined;
  const array = isRefUsage(param) ? param.usage.array : undefined;

  if (!ref.id) {
    throw new Error('Cannot create query parameter schema: missing ref id.');
  }

  let schema: Record<string, unknown> = { $ref: `#pending/${ref.id}` };

  if (array === true) {
    schema = {
      type: 'array',
      items: schema,
    };
  }

  if (nullable === true) {
    return {
      anyOf: [schema, { type: 'null' }],
    };
  }

  return schema;
}

function isOptional(param: RouteParameterFieldValue): boolean {
  const required = isRefUsage(param) ? getRefRequired(param) : undefined;
  return required === false;
}

export function isRequiredForQuery(param: QueryParameterFieldValue): boolean {
  const required = isRefUsage(param) ? getRefRequired(param) : undefined;
  return required === true;
}

function isParameterMap(value: unknown): value is RouteParameterMap {
  return !!value && typeof value === 'object' && !Array.isArray(value) && !('schema' in value) && !('kind' in value);
}

function unwrapObjectSchema(value: unknown): { properties?: Record<string, unknown>; required?: string[] } | undefined {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return undefined;

  if ('properties' in value) {
    return value as {
      properties?: Record<string, unknown>;
      required?: string[];
    };
  }

  return undefined;
}

function isRequired(name: string, required: string[] | undefined): boolean {
  return required?.includes(name) ?? false;
}

function isComponentRefInput(value: unknown): value is ComponentRef | RefUsage<ComponentRef> {
  if (!value || typeof value !== 'object') return false;
  if ('kind' in value && value.kind === RefKind.component) return true;
  if (isRefUsage(value) && value.ref.kind === RefKind.component) return true;

  return false;
}

function compileComponentRefQueryParameters(
  schema: ComponentRef | RefUsage<ComponentRef>,
  resolver: RefResolver,
  contract?: VersionContract,
): unknown[] {
  const ref = isRefUsage(schema) ? schema.ref : schema;
  const componentRef = ref as ComponentRef;

  const definition = findSchemaComponentDefinition(componentRef.id, contract);

  if (!definition) {
    throw new Error(`Unable to expand query component ref ${componentRef.id}: component definition not found`);
  }

  const fieldMap = collectQueryFieldsFromSchemaComponentValue(definition.value, contract);

  return fieldMap.map((item) => {
    if (!isQueryParameterFieldValue(item.field)) {
      throw new Error(
        `Query component field "${item.name}" must resolve to a PropertyRef, ModelRef, ComponentRef, or matching RefUsage. Got: ${describeValue(item.field)}`,
      );
    }

    return {
      name: item.name,
      in: 'query',
      required: item.required,
      schema: compileParameterField(item.field),
    };
  });
}

function findSchemaComponentDefinition(
  refId: string,
  contract?: VersionContract,
): { name: string; value: SchemaComponentValue; isShared?: boolean } | undefined {
  if (!contract) return undefined;

  for (const registry of contract.schemaComponents) {
    for (const definition of registry.definitions) {
      const componentRef = registry.ref[definition.name];

      if (componentRef.id === refId) {
        return { ...definition, isShared: true };
      }
    }
  }

  for (const resource of contract.resources) {
    for (const registry of resource.schemaComponents) {
      for (const definition of registry.definitions) {
        const componentRef = registry.ref[definition.name];

        if (componentRef.id === refId) {
          return { ...definition, isShared: false };
        }
      }
    }
  }

  return undefined;
}

export function collectQueryFieldsFromSchemaComponentValue(
  value: SchemaComponentValue,
  contract?: VersionContract,
  sourceSchema?: string,
  baseSource?: FieldSourceMetadata,
): CollectedQueryField[] {
  if (isComponentFieldMap(value)) {
    return Object.entries(value).map(([name, field]) => {
      return createCollectedQueryField(name, field, baseSource);
    });
  }

  if (isEngineRef(value)) {
    if (value.kind === RefKind.component) {
      const definition = findSchemaComponentDefinition(value.id, contract);

      if (definition) {
        const componentSource = getSourceMetadataFromRef(value, 'base');

        return collectQueryFieldsFromSchemaComponentValue(definition.value, contract, definition.name, componentSource);
      }
    }

    throw new Error(`Cannot expand query component with ref kind: ${value.kind}`);
  }

  if (isRefUsage(value) && isComponentRef(value.ref)) {
    const definition = findSchemaComponentDefinition(value.ref.id, contract);

    if (!definition) {
      throw new Error(`Cannot find component definition for ref: ${value.ref.id}`);
    }

    const baseSource = value.usage.composition?.base ?? getSourceMetadataFromRef(value.ref, 'base');

    const baseFields = collectQueryFieldsFromSchemaComponentValue(definition.value, contract, definition.name, baseSource);

    appendExtensionQueryFields(baseFields, value.usage.extendWith);

    return baseFields;
  }

  if (isRefUsage(value)) {
    const baseSource = value.usage.composition?.base ?? getSourceMetadataFromRef(value.ref, 'base');

    const baseFields = collectQueryFieldsFromSchemaComponentValue(value.ref, contract, sourceSchema, baseSource);

    appendExtensionQueryFields(baseFields, value.usage.extendWith);

    return baseFields;
  }

  return [];
}

function appendExtensionQueryFields(baseFields: CollectedQueryField[], extendWith: ExtendWithInput | undefined): void {
  const extensionFields = normalizeExtendWithInputWithSource(extendWith);

  if (!extensionFields) return;

  for (const [name, field] of Object.entries(extensionFields.fields)) {
    baseFields.push(
      createCollectedQueryField(name, field, {
        ...extensionFields.source,
        origin: extensionFields.source?.origin ?? 'extension',
      }),
    );
  }
}

function createCollectedQueryField(name: string, field: unknown, baseSource?: FieldSourceMetadata): CollectedQueryField {
  if (!isQueryParameterFieldValue(field)) {
    throw new Error(
      `Query component field "${name}" must be a PropertyRef, ModelRef, ComponentRef, or matching RefUsage. Got: ${describeValue(field)}`,
    );
  }

  const ref = isRefUsage(field) ? field.ref : field;
  const source = createQueryFieldSource(ref, name, baseSource);

  return {
    name,
    field,
    required: isRequiredForQuery(field),
    source,
  };
}

function createQueryFieldSource(
  ref: PropertyRef | ModelRef | ComponentRef,
  fieldName: string,
  baseSource?: FieldSourceMetadata,
): FieldSourceMetadata {
  const source = baseSource && baseSource.origin !== 'inline' ? baseSource : getSourceMetadataFromRef(ref, 'inline');

  if (isPropertyRef(ref)) {
    return {
      ...source,
      propertyRefId: ref.id,
      fieldKey: ref.propertyKey,
      propertyResource: ref.meta?.resource ? (ref.meta.resource as XCodegenResourceMeta).name : undefined,
    };
  }

  if (isComponentRef(ref)) {
    return {
      ...source,
      sourceRefId: ref.id,
      sourceSchemaName: ref.name,
      fieldKey: fieldName,
      propertyResource: ref.meta?.resource ? (ref.meta.resource as XCodegenResourceMeta).name : undefined,
    };
  }

  return {
    ...source,
    propertyRefId: ref.id,
    fieldKey: fieldName,
    propertyResource: ref.meta?.resource ? (ref.meta.resource as XCodegenResourceMeta).name : undefined,
  };
}

function isComponentFieldMap(value: unknown): value is ComponentFieldMap {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return false;
  if (isEngineRef(value)) return false;
  if (isRefUsage(value)) return false;

  return true;
}

function isQueryParameterFieldValue(value: unknown): value is QueryParameterFieldValue {
  if (isPropertyRef(value)) return true;
  if (isModelRef(value)) return true;
  if (isComponentRef(value)) return true;

  if (isRefUsage(value)) {
    return isPropertyRef(value.ref) || isModelRef(value.ref) || isComponentRef(value.ref);
  }

  return false;
}

function isModelRef(value: unknown): value is ModelRef {
  return (
    !!value &&
    typeof value === 'object' &&
    !Array.isArray(value) &&
    'kind' in value &&
    value.kind === RefKind.model &&
    'modelKey' in value &&
    'fields' in value
  );
}

function describeValue(value: unknown): string {
  if (!value || typeof value !== 'object') return typeof value;

  if ('kind' in value) {
    return `kind:${String((value as { kind: unknown }).kind)}`;
  }

  return 'object';
}
