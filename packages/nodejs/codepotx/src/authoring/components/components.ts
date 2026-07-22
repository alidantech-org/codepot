import { EngineIdPart, createEngineId } from '../core/engine-id';
import { normalizeInfo } from '../core/normalize';
import { RefKind } from '../refs/ref-kind';
import { withRefMethods } from '../refs/ref-methods';
import type { ComponentRef, ParameterRef, RequestBodyRef, ResponseRef } from '../refs/ref.types';
import type { RefUsage, SchemaProjectionDefinition } from '../refs/ref-usage.types';
import { z } from '../schema/z-compat';
import type {
  DefineComponentOptions,
  ParameterComponentInput,
  ParameterComponentRegistry,
  RequestBodyComponentInput,
  RequestBodyComponentRegistry,
  ResponseComponentInput,
  ResponseComponentRegistry,
  SchemaComponentDefinition,
  SchemaComponentRegistry,
  SchemaComponentValue,
} from './component.types';

export function createSchemaComponentRegistry(name: string): SchemaComponentRegistry {
  return { name, definitions: [], ref: {} };
}

export function defineSchemas<const TInput extends Record<string, SchemaComponentValue>>(
  options: DefineComponentOptions,
  input: TInput,
  target?: SchemaComponentRegistry,
): SchemaComponentRegistry<TInput> {
  const definitions = Object.entries(input).map(([name, value]) => normalizeSchemaDefinition(options, name, value));
  const ref = Object.fromEntries(definitions.map((definition) => [
    definition.name,
    createSchemaRef(options, definition),
  ])) as SchemaComponentRegistry<TInput>['ref'];

  if (target) {
    for (const definition of definitions) {
      if (target.definitions.some((item) => item.name === definition.name)) {
        throw new Error(`Duplicate schema component "${definition.name}" in registry "${target.name}".`);
      }
    }
    target.definitions.push(...definitions);
    Object.assign(target.ref, ref);
  }

  return { name: options.name, definitions, ref };
}

export function defineParameters<const TInput extends Record<string, ParameterComponentInput>>(
  options: DefineComponentOptions,
  input: TInput,
): ParameterComponentRegistry<TInput> {
  const definitions = Object.entries(input).map(([key, value]) => ({ key, ...value }));
  const ref = Object.fromEntries(definitions.map((definition) => [definition.key, {
    id: scopedId(options, EngineIdPart.component, 'parameter', definition.key),
    name: definition.key,
    kind: RefKind.parameter,
    parameterKey: definition.key,
    meta: metadata(options, 'parameter'),
  } satisfies ParameterRef])) as ParameterComponentRegistry<TInput>['ref'];
  return { name: options.name, definitions, ref };
}

export function defineRequestBodies<const TInput extends Record<string, RequestBodyComponentInput>>(
  options: DefineComponentOptions,
  input: TInput,
): RequestBodyComponentRegistry<TInput> {
  const definitions = Object.entries(input).map(([name, value]) => ({ name, ...value }));
  const ref = Object.fromEntries(definitions.map((definition) => [definition.name, {
    id: scopedId(options, EngineIdPart.component, 'request-body', definition.name),
    name: definition.name,
    kind: RefKind.requestBody,
    requestBodyKey: definition.name,
    meta: metadata(options, 'requestBody'),
  } satisfies RequestBodyRef])) as RequestBodyComponentRegistry<TInput>['ref'];
  return { name: options.name, definitions, ref };
}

export function defineResponses<const TInput extends Record<string, ResponseComponentInput>>(
  options: DefineComponentOptions,
  input: TInput,
): ResponseComponentRegistry<TInput> {
  const definitions = Object.entries(input).map(([name, value]) => ({ name, ...value }));
  const ref = Object.fromEntries(definitions.map((definition) => [definition.name, {
    id: scopedId(options, EngineIdPart.component, 'response', definition.name),
    name: definition.name,
    kind: RefKind.response,
    responseKey: definition.name,
    meta: metadata(options, 'response'),
  } satisfies ResponseRef])) as ResponseComponentRegistry<TInput>['ref'];
  return { name: options.name, definitions, ref };
}

function normalizeSchemaDefinition(
  options: DefineComponentOptions,
  name: string,
  raw: SchemaComponentValue,
): SchemaComponentDefinition {
  const unpacked = isSchemaWrapper(raw) ? raw.schema : raw;
  const info = isSchemaWrapper(raw) ? normalizeInfo(raw.info) : undefined;
  if (!isProjection(unpacked)) {
    const definition = { name, value: unpacked, ...(info ? { info } : {}) };
    options.state.schemaDefinitionsByRefId.set(scopedId(options, EngineIdPart.component, 'schema', name), definition);
    return definition;
  }

  const source = options.state.schemaDefinitionsByRefId.get(unpacked.sourceRefId) as SchemaComponentDefinition | undefined;
  if (!source) throw new Error(`Cannot create projection schema "${name}". Source schema "${unpacked.source}" was not found.`);
  let fields = resolveFields(options, source);
  let required = requiredKeys(fields);
  const steps = unpacked.steps ?? [{ mode: unpacked.mode, ...(unpacked.fields ? { fields: unpacked.fields } : {}) }];
  for (const step of steps) {
    for (const key of step.fields ?? []) {
      if (!(key in fields)) throw new Error(`Projection schema "${name}" references unknown field "${key}".`);
    }
    if (step.mode === 'partial') required = [];
    else if (step.mode === 'pick') {
      const selected = new Set(step.fields ?? []);
      fields = Object.fromEntries(Object.entries(fields).filter(([key]) => selected.has(key)));
      required = required.filter((key) => selected.has(key));
    } else {
      const omitted = new Set(step.fields ?? []);
      fields = Object.fromEntries(Object.entries(fields).filter(([key]) => !omitted.has(key)));
      required = required.filter((key) => !omitted.has(key));
    }
  }
  const definition: SchemaComponentDefinition = {
    name,
    value: fields,
    required,
    projection: {
      source: unpacked.source,
      rootSource: source.projection?.rootSource ?? source.projection?.source ?? unpacked.source,
      mode: unpacked.mode,
      ...(unpacked.fields ? { fields: unpacked.fields } : {}),
      ...(steps.length > 1 ? { steps } : {}),
    },
    ...(info ? { info } : {}),
  };
  options.state.schemaDefinitionsByRefId.set(scopedId(options, EngineIdPart.component, 'schema', name), definition);
  return definition;
}

function createSchemaRef(options: DefineComponentOptions, definition: SchemaComponentDefinition): ComponentRef & ReturnType<typeof withRefMethods<ComponentRef>> {
  const id = scopedId(options, EngineIdPart.component, 'schema', definition.name);
  options.state.schemaDefinitionsByRefId.set(id, definition);
  return withRefMethods<ComponentRef>({
    id,
    name: definition.name,
    kind: RefKind.component,
    componentKey: definition.name,
    meta: metadata(options, 'dto'),
  }, { toZod: () => schemaDefinitionToZod(options, definition) }) as ComponentRef & ReturnType<typeof withRefMethods<ComponentRef>>;
}

function schemaDefinitionToZod(options: DefineComponentOptions, definition: SchemaComponentDefinition): z.ZodTypeAny {
  const fields = resolveFields(options, definition);
  const shape: Record<string, z.ZodTypeAny> = {};
  for (const [key, value] of Object.entries(fields)) shape[key] = valueToZod(options, value);
  return z.object(shape);
}

function valueToZod(options: DefineComponentOptions, value: unknown): z.ZodTypeAny {
  if (value && typeof value === 'object' && 'safeParse' in value && 'parse' in value) return value as z.ZodTypeAny;
  if (value && typeof value === 'object' && 'zod' in value && typeof value.zod === 'function') return value.zod() as z.ZodTypeAny;
  if (value && typeof value === 'object' && 'ref' in value) {
    const usage = value as RefUsage<ComponentRef>;
    let schema = valueToZod(options, usage.ref);
    if (usage.usage.array) schema = z.array(schema);
    if (usage.usage.nullable) schema = z.nullable(schema);
    if (usage.usage.required === false) schema = z.optional(schema);
    return schema;
  }
  if (value && typeof value === 'object' && 'kind' in value) {
    const kind = (value as { readonly kind: string }).kind;
    if (kind === 'primitive') return (value as unknown as { readonly zod: z.ZodTypeAny }).zod;
    if (kind === 'literal') return z.literal((value as unknown as { readonly value: string | number | boolean | null }).value);
    if (kind === 'composite') return z.object(Object.fromEntries(Object.entries((value as unknown as { readonly fields: Record<string, unknown> }).fields).map(([key, item]) => [key, valueToZod(options, item)])));
    if (kind === 'record') return z.record(z.string(), valueToZod(options, (value as unknown as { readonly value: unknown }).value));
    if (kind === 'oneOf' || kind === 'anyOf') return z.union((value as unknown as { readonly values: readonly unknown[] }).values.map((item) => valueToZod(options, item)) as [z.ZodTypeAny, z.ZodTypeAny, ...z.ZodTypeAny[]]);
  }
  return z.unknown();
}

function resolveFields(options: DefineComponentOptions, definition: SchemaComponentDefinition): Record<string, unknown> {
  if (isPlainFields(definition.value)) return { ...definition.value };
  if (definition.value && typeof definition.value === 'object' && 'ref' in definition.value) {
    const usage = definition.value as RefUsage<ComponentRef>;
    const base = options.state.schemaDefinitionsByRefId.get(usage.ref.id) as SchemaComponentDefinition | undefined;
    if (!base) return {};
    const baseFields = resolveFields(options, base);
    const extension = usage.usage.extendWith;
    return isPlainFields(extension) ? { ...baseFields, ...extension } : baseFields;
  }
  return {};
}

function requiredKeys(fields: Record<string, unknown>): string[] {
  return Object.entries(fields).filter(([, value]) => !(value && typeof value === 'object' && 'usage' in value && (value as { readonly usage?: { readonly required?: boolean } }).usage?.required === false)).map(([key]) => key);
}

function isProjection(value: unknown): value is SchemaProjectionDefinition<string, Record<string, unknown>, 'partial' | 'pick' | 'omit'> {
  return Boolean(value && typeof value === 'object' && 'kind' in value && value.kind === 'schema-projection-definition');
}
function isSchemaWrapper(value: SchemaComponentValue): value is { readonly schema: import('./component.types').ComponentFieldValue; readonly info?: import('../core/authoring.types').InfoInput } {
  return Boolean(value && typeof value === 'object' && 'schema' in value);
}
function isPlainFields(value: unknown): value is Record<string, unknown> {
  return Boolean(value && typeof value === 'object' && !Array.isArray(value) && !('kind' in value) && !('ref' in value) && !('safeParse' in value));
}
function scopedId(options: DefineComponentOptions, ...parts: readonly string[]): string {
  return options.resource ? createEngineId(EngineIdPart.resource, options.resource.name, ...parts) : createEngineId(...parts);
}
function metadata(options: DefineComponentOptions, kind: string): { readonly kind: string; readonly shared?: boolean; readonly resource?: { readonly name: string; readonly path: readonly string[] } } {
  return options.resource
    ? { kind, resource: { name: options.resource.alias, path: options.resource.folders } }
    : { kind, shared: true };
}
