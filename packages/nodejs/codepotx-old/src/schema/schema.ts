import type { z } from 'zod';
import { SchemaKind } from './schema-kind.js';
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
  SchemaBehaviorOptions,
  SchemaField,
  SchemaFieldMap,
} from './schema.types.js';
import type { ComponentRef, ModelRef, PropertyRef } from '../refs/ref.types.js';
import type { RefUsage } from '../refs/ref-usage.types.js';

export interface CompositeOptions extends SchemaBehaviorOptions {}

export const schema = {
  primitive(zod: z.ZodTypeAny): PrimitiveSchemaField {
    return {
      kind: SchemaKind.primitive,
      zod,
    };
  },

  composite(fields: SchemaFieldMap, options: CompositeOptions = {}): CompositeSchemaField {
    return {
      kind: SchemaKind.composite,
      fields,
      required: options.required,
      nullable: options.nullable,
      description: options.description,
    };
  },

  ref(
    ref: PropertyRef | ModelRef | ComponentRef | RefUsage<PropertyRef> | RefUsage<ModelRef> | RefUsage<ComponentRef>,
    options: SchemaBehaviorOptions = {},
  ): RefSchemaField {
    return {
      kind: SchemaKind.ref,
      ref,
      required: options.required,
      nullable: options.nullable,
      description: options.description,
    };
  },

  record(value: SchemaField, options: SchemaBehaviorOptions = {}): RecordSchemaField {
    return {
      kind: SchemaKind.record,
      value,
      required: options.required,
      nullable: options.nullable,
      description: options.description,
    };
  },

  literal(value: string | number | boolean | null, options: SchemaBehaviorOptions = {}): LiteralSchemaField {
    return {
      kind: SchemaKind.literal,
      value,
      required: options.required,
      nullable: options.nullable,
      description: options.description,
    };
  },

  oneOf(values: SchemaField[], options: SchemaBehaviorOptions = {}): OneOfSchemaField {
    return {
      kind: SchemaKind.oneOf,
      values,
      required: options.required,
      nullable: options.nullable,
      description: options.description,
    };
  },

  anyOf(values: SchemaField[], options: SchemaBehaviorOptions = {}): AnyOfSchemaField {
    return {
      kind: SchemaKind.anyOf,
      values,
      required: options.required,
      nullable: options.nullable,
      description: options.description,
    };
  },

  file(options: SchemaBehaviorOptions = {}): FileSchemaField {
    return {
      kind: SchemaKind.file,
      required: options.required,
      nullable: options.nullable,
      description: options.description,
    };
  },

  noContent(options: SchemaBehaviorOptions = {}): NoContentSchemaField {
    return {
      kind: SchemaKind.noContent,
      required: options.required,
      nullable: options.nullable,
      description: options.description,
    };
  },
} as const;
