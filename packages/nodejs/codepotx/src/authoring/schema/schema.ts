import type * as z4 from 'zod/v4/core';

import { SchemaKind } from './schema-kind';
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
  SchemaReferenceInput,
} from './schema.types';
import { z } from './z-compat';
import type { CodepotZodCompatibility } from './z-compat';

export interface CompositeOptions extends SchemaBehaviorOptions {}

export interface CodepotSchemaHelpers {
  primitive<TSchema extends z4.$ZodType>(zod: TSchema): PrimitiveSchemaField<TSchema>;
  composite(fields: SchemaFieldMap, options?: CompositeOptions): CompositeSchemaField;
  ref(ref: SchemaReferenceInput, options?: SchemaBehaviorOptions): RefSchemaField;
  record(value: SchemaField, options?: SchemaBehaviorOptions): RecordSchemaField;
  literal(value: string | number | boolean | null, options?: SchemaBehaviorOptions): LiteralSchemaField;
  oneOf(values: readonly SchemaField[], options?: SchemaBehaviorOptions): OneOfSchemaField;
  anyOf(values: readonly SchemaField[], options?: SchemaBehaviorOptions): AnyOfSchemaField;
  file(options?: SchemaBehaviorOptions): FileSchemaField;
  noContent(options?: SchemaBehaviorOptions): NoContentSchemaField;
}

export type CodepotSchemaNamespace = Omit<
  CodepotZodCompatibility,
  keyof CodepotSchemaHelpers
> & CodepotSchemaHelpers;

const codepotSchema: CodepotSchemaHelpers = {
  primitive<TSchema extends z4.$ZodType>(zod: TSchema): PrimitiveSchemaField<TSchema> {
    return { kind: SchemaKind.primitive, zod };
  },

  composite(fields: SchemaFieldMap, options: CompositeOptions = {}): CompositeSchemaField {
    return { kind: SchemaKind.composite, fields, ...options };
  },

  ref(ref: SchemaReferenceInput, options: SchemaBehaviorOptions = {}): RefSchemaField {
    return { kind: SchemaKind.ref, ref, ...options };
  },

  record(value: SchemaField, options: SchemaBehaviorOptions = {}): RecordSchemaField {
    return { kind: SchemaKind.record, value, ...options };
  },

  literal(value: string | number | boolean | null, options: SchemaBehaviorOptions = {}): LiteralSchemaField {
    return { kind: SchemaKind.literal, value, ...options };
  },

  oneOf(values: readonly SchemaField[], options: SchemaBehaviorOptions = {}): OneOfSchemaField {
    return { kind: SchemaKind.oneOf, values, ...options };
  },

  anyOf(values: readonly SchemaField[], options: SchemaBehaviorOptions = {}): AnyOfSchemaField {
    return { kind: SchemaKind.anyOf, values, ...options };
  },

  file(options: SchemaBehaviorOptions = {}): FileSchemaField {
    return { kind: SchemaKind.file, ...options };
  },

  noContent(options: SchemaBehaviorOptions = {}): NoContentSchemaField {
    return { kind: SchemaKind.noContent, ...options };
  },
};

/** Preferred Codepot schema namespace: curated Zod constructors plus Codepot composition helpers. */
export const schema: CodepotSchemaNamespace = Object.freeze({
  ...z,
  ...codepotSchema,
});
