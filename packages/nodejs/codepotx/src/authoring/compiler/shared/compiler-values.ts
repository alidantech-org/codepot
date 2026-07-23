import type {
  CompiledDocumentation,
  Diagnostic,
  JsonObject,
  JsonValue,
} from '@/contract/index';
import { isRefUsage } from '../../refs/ref-methods';
import { RefKind } from '../../refs/ref-kind';
import type { EngineRef } from '../../refs/ref.types';
import { SchemaKind } from '../../schema/schema-kind';
import type { SchemaField } from '../../schema/schema.types';

/** Strict dynamic-object view used only while normalizing authored values. */
export interface DynamicObject extends Record<string, unknown> {
  readonly _def?: unknown;
  readonly _zod?: unknown;
  readonly aliasOf?: unknown;
  readonly date?: unknown;
  readonly def?: unknown;
  readonly description?: unknown;
  readonly element?: unknown;
  readonly entries?: unknown;
  readonly exact?: unknown;
  readonly format?: unknown;
  readonly global?: unknown;
  readonly id?: unknown;
  readonly key?: unknown;
  readonly kind?: unknown;
  readonly mode?: unknown;
  readonly name?: unknown;
  readonly oneOf?: unknown;
  readonly owner?: unknown;
  readonly range?: unknown;
  readonly required?: unknown;
  readonly resource?: unknown;
  readonly safeParse?: unknown;
  readonly schema?: unknown;
  readonly search?: unknown;
  readonly sort?: unknown;
  readonly source?: unknown;
  readonly sourceRefId?: unknown;
  readonly summary?: unknown;
  readonly type?: unknown;
  readonly typeName?: unknown;
  readonly value?: unknown;
  readonly values?: unknown;
}

export function dynamicObject(value: unknown): value is DynamicObject {
  return Boolean(value && typeof value === 'object' && !Array.isArray(value));
}

export function jsonObject(value: unknown): JsonObject {
  const result = jsonValue(value);
  return dynamicObject(result) ? result as JsonObject : {};
}

export function jsonValue(value: unknown): JsonValue {
  if (
    value === null
    || typeof value === 'string'
    || typeof value === 'number'
    || typeof value === 'boolean'
  ) return value;
  if (typeof value === 'bigint') return value.toString();
  if (Array.isArray(value)) return value.map(jsonValue);
  if (value instanceof Date) return value.toISOString();
  if (dynamicObject(value)) {
    return Object.fromEntries(
      Object.entries(value)
        .filter(([, item]) =>
          item !== undefined
          && typeof item !== 'function'
          && typeof item !== 'symbol',
        )
        .map(([key, item]) => [key, jsonValue(item)]),
    );
  }
  return String(value);
}

export function docsProperty(value: unknown): { readonly docs?: CompiledDocumentation } {
  const compiled = docs(value);
  return compiled ? { docs: compiled } : {};
}

function docs(value: unknown): CompiledDocumentation | undefined {
  if (!dynamicObject(value)) return undefined;
  const summary = typeof value.summary === 'string' ? value.summary : undefined;
  const description = typeof value.description === 'string'
    ? value.description
    : undefined;
  return summary || description
    ? {
        ...(summary ? { summary } : {}),
        ...(description ? { description } : {}),
      }
    : undefined;
}

export function owner(value: unknown): string {
  if (!dynamicObject(value)) return 'global';
  if (value.global === true) return 'global';
  const resource = dynamicObject(value.resource) ? value.resource : undefined;
  return resource && typeof resource.name === 'string'
    ? resource.name
    : 'global';
}

export function accessRef(value: unknown): string | undefined {
  return dynamicObject(value)
    && typeof value.key === 'string'
    && value.owner !== undefined
    ? `access:${owner(value.owner)}:${value.key}`
    : undefined;
}

export function required(value: unknown): boolean {
  if (isRefUsage(value)) return value.usage.required ?? true;
  return dynamicObject(value) && typeof value.required === 'boolean'
    ? value.required
    : true;
}

export function bodySchema(value: unknown): unknown {
  return dynamicObject(value) && value.schema !== undefined ? value.schema : value;
}

export function responseSchema(value: unknown): unknown {
  return dynamicObject(value) && value.schema !== undefined ? value.schema : value;
}

export function noContent(value: unknown): boolean {
  const schema = responseSchema(value);
  return isSchemaField(schema) && schema.kind === SchemaKind.noContent;
}

export function joinRoutePath(base: string, path: string): string {
  const left = base === '/' ? '' : base.replace(/\/$/, '');
  const right = path === '/' ? '' : path.replace(/^\//, '');
  return `${left}/${right}`.replace(/\/+/g, '/') || '/';
}

export function cardinality(
  value: string,
): 'oneToOne' | 'oneToMany' | 'manyToOne' | 'manyToMany' {
  if (value === 'belongsTo') return 'manyToOne';
  if (value === 'hasMany') return 'oneToMany';
  if (value === 'manyToMany') return 'manyToMany';
  return 'oneToOne';
}

export function deleteBehavior(value: unknown): string | undefined {
  if (!dynamicObject(value)) return undefined;
  return Object.keys(value).find((key) => value[key] === true);
}

export function refId(value: unknown): string {
  if (isRefUsage(value)) return value.ref.id;
  return isEngineRef(value) ? value.id : 'unknown';
}

export function isRef(value: unknown): boolean {
  return isRefUsage(value) || isEngineRef(value);
}

export function isEngineRef(value: unknown): value is EngineRef {
  return dynamicObject(value)
    && typeof value.id === 'string'
    && typeof value.name === 'string'
    && Object.values(RefKind).includes(value.kind as never);
}

export function isSchemaField(value: unknown): value is SchemaField {
  return dynamicObject(value)
    && typeof value.kind === 'string'
    && Object.values(SchemaKind).includes(value.kind as never);
}

export function isProjection(value: unknown): value is {
  readonly source: string;
  readonly sourceRefId: string;
  readonly mode: string;
  readonly fields?: readonly string[];
  readonly steps?: readonly unknown[];
} {
  return dynamicObject(value)
    && value.kind === 'schema-projection-definition'
    && typeof value.source === 'string'
    && typeof value.sourceRefId === 'string'
    && typeof value.mode === 'string';
}

export function isZod(value: unknown): value is DynamicObject {
  return dynamicObject(value)
    && (
      value._zod !== undefined
      || value._def !== undefined
      || typeof value.safeParse === 'function'
    );
}

export function zodDefinition(value: DynamicObject): DynamicObject {
  const zod = dynamicObject(value._zod) ? value._zod : undefined;
  if (zod && dynamicObject(zod.def)) return zod.def;
  return dynamicObject(value._def) ? value._def : {};
}

export function primitive(
  value: unknown,
): 'string' | 'number' | 'integer' | 'boolean' | 'bigint' | 'date' | 'null' | 'unknown' {
  if (value === null) return 'null';
  if (typeof value === 'string') return 'string';
  if (typeof value === 'number') return Number.isInteger(value) ? 'integer' : 'number';
  if (typeof value === 'boolean') return 'boolean';
  if (typeof value === 'bigint') return 'bigint';
  if (value instanceof Date) return 'date';
  return 'unknown';
}

export function authoringDiagnostic(
  code: string,
  severity: Diagnostic['severity'],
  message: string,
): Diagnostic {
  return { code, severity, layer: 'authoring', message };
}
