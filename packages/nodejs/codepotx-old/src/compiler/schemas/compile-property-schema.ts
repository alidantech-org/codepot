import type { SchemaCompositionFieldValue } from '../../schema/schema.types.js';
import { SchemaKind } from '../../schema/schema-kind.js';
import type {
  AnyOfSchemaField,
  CompositeSchemaField,
  FileSchemaField,
  LiteralSchemaField,
  NoContentSchemaField,
  OneOfSchemaField,
  PrimitiveSchemaField,
  RecordSchemaField,
  RefSchemaField,
  SchemaField,
} from '../../schema/schema.types.js';
import { isRefUsage, getRefRequired, getRefNullable, getRefArray, getRefExtendWith } from '../../validation/ref-usage-guards.js';
import { zodToOpenApiSchema, type ZodSchemaMode } from './zod-to-openapi-schema.js';
import { normalizeExtendWithInput } from './normalize-extend-with.js';

export function compilePropertySchema(field: SchemaField, mode: ZodSchemaMode = 'output'): unknown {
  if (field.kind === SchemaKind.primitive) {
    return compilePrimitive(field, mode);
  }

  if (field.kind === SchemaKind.composite) {
    return compileComposite(field, mode);
  }

  if (field.kind === SchemaKind.ref) {
    return compileRef(field, mode);
  }

  if (field.kind === SchemaKind.record) {
    return compileRecord(field, mode);
  }

  if (field.kind === SchemaKind.literal) {
    return compileLiteral(field, mode);
  }

  if (field.kind === SchemaKind.oneOf) {
    return compileOneOf(field, mode);
  }

  if (field.kind === SchemaKind.anyOf) {
    return compileAnyOf(field, mode);
  }

  if (field.kind === SchemaKind.file) {
    return compileFile(field, mode);
  }

  if (field.kind === SchemaKind.noContent) {
    return compileNoContent(field, mode);
  }

  throw new Error(`Unknown schema kind: ${(field as { kind: string }).kind}`);
}

function compilePrimitive(field: PrimitiveSchemaField, mode: ZodSchemaMode): unknown {
  const schema = {
    ...inferKnownZodStringSchema(field.zod),
    ...asObject(zodToOpenApiSchema(field.zod, mode)),
    description: field.description,
  };

  return applyNullable(
    schema,
    field.nullable,
  );
}

function compileComposite(field: CompositeSchemaField, mode: ZodSchemaMode): unknown {
  const required = getRequiredKeys(field.fields);

  const schema: Record<string, unknown> = {
    type: 'object',
    description: field.description,
    properties: Object.fromEntries(Object.entries(field.fields).map(([key, value]) => [key, compilePropertySchema(value, mode)])),
  };

  if (required.length > 0) {
    schema.required = required;
  }

  return applyNullable(schema, field.nullable);
}

function compileRef(field: RefSchemaField, mode: ZodSchemaMode): unknown {
  let schema: Record<string, unknown>;
  const ref = isRefUsage(field.ref) ? field.ref.ref : field.ref;
  const refUsage = isRefUsage(field.ref) ? field.ref : undefined;
  const source = refUsage?.usage.source;

  // Step 1: Resolve base ref to OpenAPI $ref
  schema = { $ref: `#pending/${ref.id}` };

  // Step 2: Apply extendWith
  const extendWith = refUsage ? getRefExtendWith(refUsage) : undefined;
  const normalizedExtendWith = normalizeExtendWithInput(extendWith);
  if (normalizedExtendWith && Object.keys(normalizedExtendWith).length > 0) {
    const entries = Object.entries(normalizedExtendWith) as Array<[string, SchemaCompositionFieldValue]>;
    schema = {
      allOf: [
        schema,
        {
          type: 'object',
          properties: Object.fromEntries(entries.map(([key, value]) => [key, compilePropertySchema(wrapAsRefSchemaField(value), mode)])),
        },
      ],
    };
  }

  // Step 3: Apply array
  const isArray = refUsage ? getRefArray(refUsage) : false;
  if (isArray) {
    schema = {
      type: 'array',
      items: schema,
    };
  }

  // Step 4: Apply nullable from usage
  if (refUsage && getRefNullable(refUsage)) {
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

  // Step 5: Apply description from field options
  if (field.description) {
    schema.description = field.description;
  }

  if (source) {
    schema['x-codegen'] = {
      source: normalizeFieldSourceMetadata(source),
    };
  }

  // Step 6: Apply nullable from field options (outer wrapper)
  return applyNullable(schema, field.nullable);
}

function wrapAsRefSchemaField(ref: SchemaCompositionFieldValue): RefSchemaField {
  return {
    kind: SchemaKind.ref,
    ref: ref as RefSchemaField['ref'],
  };
}

function compileRecord(field: RecordSchemaField, mode: ZodSchemaMode): unknown {
  return applyNullable(
    {
      type: 'object',
      additionalProperties: compilePropertySchema(field.value, mode),
      description: field.description,
    },
    field.nullable,
  );
}

function compileLiteral(field: LiteralSchemaField, mode: ZodSchemaMode): unknown {
  const schema: Record<string, unknown> = {
    const: field.value,
    description: field.description,
  };

  if (field.value === null) {
    schema.type = 'null';
  } else if (typeof field.value === 'string') {
    schema.type = 'string';
  } else if (typeof field.value === 'number') {
    schema.type = Number.isInteger(field.value) ? 'integer' : 'number';
  } else if (typeof field.value === 'boolean') {
    schema.type = 'boolean';
  }

  return applyNullable(schema, field.nullable);
}

function compileOneOf(field: OneOfSchemaField, mode: ZodSchemaMode): unknown {
  return applyNullable(
    {
      oneOf: field.values.map((value) => compilePropertySchema(value, mode)),
      description: field.description,
    },
    field.nullable,
  );
}

function compileAnyOf(field: AnyOfSchemaField, mode: ZodSchemaMode): unknown {
  return applyNullable(
    {
      anyOf: field.values.map((value) => compilePropertySchema(value, mode)),
      description: field.description,
    },
    field.nullable,
  );
}

function compileFile(field: FileSchemaField, mode: ZodSchemaMode): unknown {
  return applyNullable(
    {
      type: 'string',
      format: 'binary',
      description: field.description,
    },
    field.nullable,
  );
}

function compileNoContent(field: NoContentSchemaField, mode: ZodSchemaMode): unknown {
  return applyNullable(
    {
      description: field.description,
    },
    field.nullable,
  );
}

function getRequiredKeys(fields: CompositeSchemaField['fields']): string[] {
  return Object.entries(fields)
    .filter(([, value]) => isRequired(value))
    .map(([key]) => key);
}

function isRequired(value: SchemaField): boolean {
  const required = getRefRequired(value);
  if (required !== undefined) return required;

  if (!isRefUsage(value) && 'required' in value && value.required !== undefined) {
    return value.required;
  }

  return true;
}

function applyNullable(schema: unknown, nullable: boolean | undefined): unknown {
  if (!nullable) return schema;

  const schemaObj = asObject(schema);

  // For OpenAPI 3.1, use type arrays for simple nullable primitives
  // This is cleaner and avoids classification issues
  if (schemaObj.type && typeof schemaObj.type === 'string') {
    const primitiveTypes = ['string', 'number', 'integer', 'boolean'];
    if (primitiveTypes.includes(schemaObj.type)) {
      const { type, ...rest } = schemaObj;
      return {
        ...rest,
        type: [type, 'null'],
      };
    }
  }

  // For complex schemas, use anyOf
  return {
    anyOf: [schema, { type: 'null' }],
  };
}

function asObject(value: unknown): Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    return {};
  }

  return value as Record<string, unknown>;
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

function inferKnownZodStringSchema(schema: unknown): Record<string, unknown> {
  const format = findZodStringFormat(schema);

  if (!format) return {};

  if (format === 'datetime' || format === 'date-time') {
    return { type: 'string', format: 'date-time' };
  }

  if (format === 'uuid') {
    return { type: 'string', format: 'uuid' };
  }

  if (format === 'email') {
    return { type: 'string', format: 'email' };
  }

  if (format === 'url' || format === 'uri') {
    return { type: 'string', format: 'uri' };
  }

  return {};
}

function findZodStringFormat(schema: unknown): string | undefined {
  const seen = new Set<unknown>();
  const stack = [schema];

  while (stack.length > 0) {
    const current = stack.pop();
    if (!current || typeof current !== 'object' || seen.has(current)) continue;
    seen.add(current);

    const record = current as Record<string, unknown>;
    const format = record.format ?? record.kind ?? record.check ?? record.type;

    if (typeof format === 'string' && isKnownStringFormat(format)) {
      return format;
    }

    for (const key of ['_def', 'def', '_zod']) {
      const child = record[key];
      if (child && typeof child === 'object') {
        stack.push(child);
      }
    }

    const checks = record.checks;
    if (Array.isArray(checks)) {
      stack.push(...checks);
    }
  }

  return undefined;
}

function isKnownStringFormat(value: string): boolean {
  return ['datetime', 'date-time', 'uuid', 'email', 'url', 'uri'].includes(value);
}
