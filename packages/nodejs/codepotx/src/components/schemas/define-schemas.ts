import { EngineIdPart, createEngineId } from '../../ids/engine-id.js';
import { RefKind } from '../../refs/ref-kind.js';
import type { ComponentRef } from '../../refs/ref.types.js';
import { withRefMethods } from '../../refs/ref-methods.js';
import type {
  RefWithUsageMethods,
  SchemaProjection,
  SchemaProjectionDefinition,
  SchemaProjectionStep,
  SchemaRefWithUsageMethods,
} from '../../refs/ref-usage.types.js';
import type { OptionalResourceContext } from '../../resource/resource-context.types.js';
import { XCodegenKind } from '../../codegen/codegen-extension.types.js';
import type {
  SchemaComponentDefinition,
  SchemaComponentRegistry,
  SchemaComponentValue,
} from './schema-component.types.js';
import { compileZodRef } from '../../zod/compile-zod-ref.js';
import type { z } from 'zod';
import { normalizeExtendWithInput } from '../../compiler/schemas/normalize-extend-with.js';
import type { ComponentFieldMap } from '../component.types.js';

export interface DefineSchemasOptions extends OptionalResourceContext {
  readonly name: string;
}

const schemaDefinitionsByRefId = new Map<string, SchemaComponentDefinition>();

export function getSchemaDefinitionByRefId(refId: string): SchemaComponentDefinition | undefined {
  return schemaDefinitionsByRefId.get(refId);
}

export function getSchemaFieldKeysByRefId(refId: string): readonly string[] {
  const definition = schemaDefinitionsByRefId.get(refId);
  if (!definition) return [];

  return Object.keys(resolveProjectionSourceFields(definition));
}

export function defineSchemas<const TInput extends Record<string, SchemaComponentValue>>(
  options: DefineSchemasOptions,
  input: TInput,
  target?: SchemaComponentRegistry,
): SchemaComponentRegistry<TInput> {
  const toZod = options.zodRegistry ? (ref: unknown): z.ZodTypeAny => compileZodRef(ref as ComponentRef, options.zodRegistry!) : undefined;
  const definitions = Object.entries(input).map(([name, value]) => normalizeSchemaDefinition(name, value as SchemaComponentValue));
  const ref = createRefs<TInput>(options, definitions, toZod);

  if (target) {
    appendDefinitions(target, definitions, ref);
  }

  return {
    name: options.name,
    definitions,
    ref,
  };
}

export function createSchemaComponentRegistry(name: string): SchemaComponentRegistry {
  return {
    name,
    definitions: [],
    ref: {},
  };
}

function appendDefinitions(
  target: SchemaComponentRegistry,
  definitions: readonly SchemaComponentDefinition[],
  ref: Record<string, RefWithUsageMethods<ComponentRef>>,
): void {
  const incoming = new Set<string>();

  for (const definition of definitions) {
    if (target.definitions.some((item) => item.name === definition.name) || incoming.has(definition.name)) {
      throw new Error(`Duplicate schema component "${definition.name}" in registry "${target.name}".`);
    }

    incoming.add(definition.name);
  }

  target.definitions.push(...definitions);
  Object.assign(target.ref, ref);
}

function createRefs<TInput extends Record<string, unknown>>(
  options: DefineSchemasOptions,
  definitions: readonly SchemaComponentDefinition[],
  toZod?: (ref: unknown) => z.ZodTypeAny,
): SchemaComponentRegistry<TInput>['ref'] {
  const entries = definitions.map((definition) => {
    return [definition.name, createSchemaRef(options, definition, toZod)] as const;
  });
  return Object.fromEntries(entries) as SchemaComponentRegistry<TInput>['ref'];
}

function createSchemaRef(
  options: DefineSchemasOptions,
  definition: SchemaComponentDefinition,
  toZod?: (ref: unknown) => z.ZodTypeAny,
): SchemaRefWithUsageMethods<ComponentRef, Record<string, unknown>> {
  const { name } = definition;
  const refId = createScopedId(options, EngineIdPart.component, 'schema', name);
  const isShared = !options.resource;

  schemaDefinitionsByRefId.set(refId, definition);

  // Register schema definition in zodRegistry if available
  if (options.zodRegistry) {
    options.zodRegistry.schemas.set(refId, definition);
  }

  return withRefMethods(
    {
      id: refId,
      name,
      kind: RefKind.component,
      componentKey: name,
      meta: {
        kind: XCodegenKind.dto,
        // Do not set role here - role is determined by route usage (query, body, response, params)
        ...(isShared ? { shared: true } : {}),
        resource: options.resource
          ? {
              name: options.resource.alias,
              path: options.resource.folders,
            }
          : undefined,
      },
    },
    { toZod },
  ) as SchemaRefWithUsageMethods<ComponentRef, Record<string, unknown>>;
}

function createScopedId(options: DefineSchemasOptions, ...parts: string[]): string {
  if (!options.resource) return createEngineId(...parts);
  return createEngineId(EngineIdPart.resource, options.resource.name, ...parts);
}

function normalizeSchemaDefinition(name: string, value: SchemaComponentValue): SchemaComponentDefinition {
  if (!isSchemaProjectionDefinition(value)) {
    return { name, value };
  }

  const sourceDefinition = schemaDefinitionsByRefId.get(value.sourceRefId);

  if (!sourceDefinition) {
    throw new Error(`Cannot create projection schema "${name}". Source schema "${value.source}" was not found.`);
  }

  const steps = resolveProjectionSteps(value);
  let fields = resolveProjectionSourceFields(sourceDefinition);
  let required = resolveProjectionSourceRequired(sourceDefinition);

  for (const step of steps) {
    validateProjectionKeys(name, value.source, fields, step.fields);
    fields = projectFields(fields, step.mode, step.fields);
    required = projectRequired(required, step.mode, step.fields);
  }

  return {
    name,
    value: fields,
    required,
    projection: {
      source: value.source,
      rootSource: sourceDefinition.projection?.rootSource ?? sourceDefinition.projection?.source ?? value.source,
      mode: value.mode,
      ...(value.fields ? { fields: value.fields } : {}),
      ...(steps.length > 1 ? { steps } : {}),
    },
  };
}

function resolveProjectionSteps(
  value: SchemaProjectionDefinition<string, Record<string, unknown>, SchemaProjection['mode']>,
): readonly SchemaProjectionStep[] {
  return value.steps ?? [{ mode: value.mode, ...(value.fields ? { fields: value.fields } : {}) }];
}

function resolveProjectionSourceFields(definition: SchemaComponentDefinition): ComponentFieldMap {
  if (isComponentFieldMap(definition.value)) {
    return { ...definition.value };
  }

  if (isRefUsageWithExtendWith(definition.value)) {
    const baseDefinition = schemaDefinitionsByRefId.get(definition.value.ref.id);

    if (!baseDefinition) {
      throw new Error(`Cannot project schema "${definition.name}". Base schema "${definition.value.ref.name}" was not found.`);
    }

    const baseFields = resolveProjectionSourceFields(baseDefinition);
    const extensionFields = normalizeExtendWithInput(definition.value.usage.extendWith);

    if (!extensionFields) {
      throw new Error(`Cannot project schema "${definition.name}". extendWith fields are not a supported field map.`);
    }

    return {
      ...baseFields,
      ...extensionFields,
    };
  }

  throw new Error(`Cannot project schema "${definition.name}". Only object schemas and extendWith schemas are supported.`);
}

function resolveProjectionSourceRequired(definition: SchemaComponentDefinition): readonly string[] {
  if (definition.required) {
    return [...definition.required];
  }

  if (isComponentFieldMap(definition.value)) {
    return getRequiredKeys(definition.value);
  }

  if (isRefUsageWithExtendWith(definition.value)) {
    const baseDefinition = schemaDefinitionsByRefId.get(definition.value.ref.id);

    if (!baseDefinition) {
      throw new Error(`Cannot project schema "${definition.name}". Base schema "${definition.value.ref.name}" was not found.`);
    }

    const baseRequired = resolveProjectionSourceRequired(baseDefinition);
    const extensionFields = normalizeExtendWithInput(definition.value.usage.extendWith);

    if (!extensionFields) {
      throw new Error(`Cannot project schema "${definition.name}". extendWith fields are not a supported field map.`);
    }

    return [...new Set([...baseRequired, ...getRequiredKeys(extensionFields)])];
  }

  throw new Error(`Cannot project schema "${definition.name}". Only object schemas and extendWith schemas are supported.`);
}

function projectFields(
  sourceFields: ComponentFieldMap,
  mode: SchemaProjection['mode'],
  selectedKeys: readonly string[] | undefined,
): ComponentFieldMap {
  if (mode === 'partial') return { ...sourceFields };

  if (!selectedKeys) {
    throw new Error(`Projection mode "${mode}" requires fields.`);
  }

  if (mode === 'pick') {
    return Object.fromEntries(selectedKeys.map((key) => [key, sourceFields[key]])) as ComponentFieldMap;
  }

  const omitted = new Set(selectedKeys);
  return Object.fromEntries(Object.entries(sourceFields).filter(([key]) => !omitted.has(key))) as ComponentFieldMap;
}

function projectRequired(
  sourceRequired: readonly string[],
  mode: SchemaProjection['mode'],
  selectedKeys: readonly string[] | undefined,
): readonly string[] {
  if (mode === 'partial') return [];

  if (!selectedKeys) {
    throw new Error(`Projection mode "${mode}" requires fields.`);
  }

  const selected = new Set(selectedKeys);

  if (mode === 'pick') {
    return sourceRequired.filter((key) => selected.has(key));
  }

  return sourceRequired.filter((key) => !selected.has(key));
}

function validateProjectionKeys(
  projectionName: string,
  sourceName: string,
  sourceFields: Record<string, unknown>,
  selectedKeys: readonly string[] | undefined,
): void {
  for (const key of selectedKeys ?? []) {
    if (!(key in sourceFields)) {
      throw new Error(`Projection schema "${projectionName}" references unknown field "${key}" on source schema "${sourceName}".`);
    }
  }
}

function isComponentFieldMap(value: unknown): value is ComponentFieldMap {
  return !!value && typeof value === 'object' && !Array.isArray(value) && !('kind' in value) && !('ref' in value);
}

function isSchemaProjectionDefinition(
  value: unknown,
): value is SchemaProjectionDefinition<string, Record<string, unknown>, SchemaProjection['mode']> {
  return (
    !!value &&
    typeof value === 'object' &&
    !Array.isArray(value) &&
    (value as { kind?: unknown }).kind === 'schema-projection-definition'
  );
}

function isRefUsageWithExtendWith(value: unknown): value is { ref: ComponentRef; usage: { extendWith: import('../../refs/ref-usage.types.js').ExtendWithInput } } {
  return (
    !!value &&
    typeof value === 'object' &&
    'ref' in value &&
    'usage' in value &&
    !!(value as { usage?: { extendWith?: unknown } }).usage?.extendWith &&
    (value as { ref?: { kind?: unknown } }).ref?.kind === RefKind.component
  );
}

function getRequiredKeys(fields: ComponentFieldMap): string[] {
  return Object.entries(fields)
    .filter(([, value]) => !isOptional(value))
    .map(([key]) => key);
}

function isOptional(value: unknown): boolean {
  return !!value && typeof value === 'object' && 'usage' in value && (value as { usage?: { required?: boolean } }).usage?.required === false;
}
