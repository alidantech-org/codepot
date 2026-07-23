import type {
  CompiledField,
  CompiledInlineSchema,
  CompiledSchemaUse,
} from '@/contract/index';
import { isRefUsage } from '../../refs/ref-methods';
import { SchemaKind } from '../../schema/schema-kind';
import type { SchemaField } from '../../schema/schema.types';
import {
  dynamicObject,
  isEngineRef,
  isProjection,
  isRef,
  isSchemaField,
  isZod,
  jsonValue,
  primitive,
  refId,
  zodDefinition,
} from '../shared/compiler-values';

export function namedSchema(value: unknown): CompiledInlineSchema {
  if (isProjection(value)) {
    return {
      kind: 'object',
      fields: [],
      extends: [value.sourceRefId],
      additionalProperties: false,
      metadata: {
        projection: {
          source: value.source,
          mode: value.mode,
          fields: value.fields ?? [],
          steps: value.steps ?? [],
        },
      },
    };
  }
  if (isRef(value)) {
    return {
      kind: 'object',
      fields: [],
      extends: [refId(value)],
      additionalProperties: false,
    };
  }
  if (isSchemaField(value)) return inlineSchema(value);
  if (dynamicObject(value) && !isZod(value)) return objectSchema(value);
  return zodSchema(value);
}

export function field(key: string, value: unknown, id: string): CompiledField {
  return {
    id,
    key,
    name: key,
    wireName: key,
    schema: schemaUse(value),
    lifecycle: {
      selectable: true,
      editable: true,
      immutable: false,
      managed: false,
    },
    query: queryMetadata(undefined),
  };
}

export function schemaUse(value: unknown): CompiledSchemaUse {
  const usage = isRefUsage(value) ? value.usage : undefined;
  const source = isRefUsage(value) ? value.ref : value;
  const requiredValue = usage?.required ?? true;
  const nullable = usage?.nullable ?? false;
  const base = isEngineRef(source)
    ? ({ kind: 'ref', ref: source.id, required: requiredValue, nullable } as const)
    : ({
        kind: 'inline',
        schema: isSchemaField(source)
          ? inlineSchema(source)
          : dynamicObject(source) && !isZod(source)
            ? objectSchema(source)
            : zodSchema(source),
        required: requiredValue,
        nullable,
      } as const);

  if (!usage?.array) return base;
  return inlineUse({ kind: 'array', items: base, constraints: [] }, requiredValue, nullable);
}

export function queryMetadata(value: unknown): CompiledField['query'] {
  const query = dynamicObject(value) ? value : {};
  const operators = [
    query.exact ? 'exact' : undefined,
    query.oneOf ? 'oneOf' : undefined,
    query.range ? 'range' : undefined,
    query.date ? 'date' : undefined,
    query.search ? 'search' : undefined,
  ].filter((item): item is string => item !== undefined);
  return {
    enabled: operators.length > 0 || query.sort === true,
    filterable: operators.some((item) => item !== 'search'),
    searchable: query.search !== undefined,
    sortable: query.sort === true,
    operators,
  };
}

export function inlineUse(
  schema: CompiledInlineSchema,
  requiredValue = true,
  nullable = false,
): CompiledSchemaUse {
  return {
    kind: 'inline',
    schema,
    required: requiredValue,
    nullable,
  };
}

function inlineSchema(value: SchemaField): CompiledInlineSchema {
  switch (value.kind) {
    case SchemaKind.primitive:
      return zodSchema(value.zod);
    case SchemaKind.composite:
      return objectSchema(value.fields);
    case SchemaKind.ref:
      return {
        kind: 'object',
        fields: [],
        extends: [refId(value.ref)],
        additionalProperties: false,
      };
    case SchemaKind.record:
      return { kind: 'record', values: schemaUse(value.value) };
    case SchemaKind.literal:
      return { kind: 'literal', value: value.value };
    case SchemaKind.oneOf:
      return {
        kind: 'union',
        mode: 'oneOf',
        variants: value.values.map(schemaUse),
      };
    case SchemaKind.anyOf:
      return {
        kind: 'union',
        mode: 'anyOf',
        variants: value.values.map(schemaUse),
      };
    case SchemaKind.file:
      return { kind: 'file', mediaTypes: ['application/octet-stream'] };
    case SchemaKind.noContent:
      return { kind: 'noContent' };
  }
}

function objectSchema(value: Readonly<Record<string, unknown>>): CompiledInlineSchema {
  return {
    kind: 'object',
    fields: Object.entries(value).map(([key, item]) =>
      field(key, item, isRef(item) ? refId(item) : `field:${key}`),
    ),
    extends: [],
    additionalProperties: false,
  };
}

function zodSchema(value: unknown): CompiledInlineSchema {
  if (!isZod(value)) {
    return { kind: 'primitive', primitive: primitive(value), constraints: [] };
  }
  const definition = zodDefinition(value);
  const kind = String(
    definition.type ?? definition.typeName ?? value.constructor.name,
  ).toLowerCase();
  if (kind.includes('array')) {
    return {
      kind: 'array',
      items: inlineUse(zodSchema(definition.element ?? definition.type)),
      constraints: [],
    };
  }
  if (kind.includes('enum')) {
    const entries = dynamicObject(definition.entries) ? definition.entries : {};
    const values = Object.values(entries).filter(
      (item): item is string | number =>
        typeof item === 'string' || typeof item === 'number',
    );
    return {
      kind: 'enum',
      valueType: values.some((item) => typeof item === 'number')
        ? 'number'
        : 'string',
      options: values.map((item) => ({ key: String(item), value: item })),
    };
  }
  if (kind.includes('literal')) {
    return {
      kind: 'literal',
      value: jsonValue(
        definition.value
          ?? (Array.isArray(definition.values) ? definition.values[0] : null),
      ),
    };
  }
  return {
    kind: 'primitive',
    primitive: kind.includes('string')
      ? 'string'
      : kind.includes('boolean')
        ? 'boolean'
        : kind.includes('bigint')
          ? 'bigint'
          : kind.includes('int')
            ? 'integer'
            : kind.includes('number')
              ? 'number'
              : kind.includes('date')
                ? 'date'
                : 'unknown',
    constraints: [],
    ...(typeof definition.format === 'string'
      ? { format: definition.format }
      : {}),
  };
}
