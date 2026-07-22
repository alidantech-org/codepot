import type * as z4 from 'zod/v4/core';

import type { SchemaKind } from './schema-kind';

export interface SchemaBehaviorOptions {
  readonly required?: boolean;
  readonly nullable?: boolean;
  readonly description?: string;
}

export interface SchemaReferenceLike {
  readonly id: string;
  readonly name: string;
  readonly kind: string;
}

export interface SchemaReferenceUsageLike<TRef extends SchemaReferenceLike = SchemaReferenceLike> {
  readonly ref: TRef;
  readonly usage: SchemaBehaviorOptions & {
    readonly array?: boolean;
    readonly extendWith?: unknown;
  };
}

export type SchemaReferenceInput = SchemaReferenceLike | SchemaReferenceUsageLike;

export interface PrimitiveSchemaField<TSchema extends z4.$ZodType = z4.$ZodType>
  extends SchemaBehaviorOptions {
  readonly kind: typeof SchemaKind.primitive;
  readonly zod: TSchema;
}

export interface CompositeSchemaField extends SchemaBehaviorOptions {
  readonly kind: typeof SchemaKind.composite;
  readonly fields: SchemaFieldMap;
}

export interface RefSchemaField extends SchemaBehaviorOptions {
  readonly kind: typeof SchemaKind.ref;
  readonly ref: SchemaReferenceInput;
}

export interface RecordSchemaField extends SchemaBehaviorOptions {
  readonly kind: typeof SchemaKind.record;
  readonly value: SchemaField;
}

export interface LiteralSchemaField extends SchemaBehaviorOptions {
  readonly kind: typeof SchemaKind.literal;
  readonly value: string | number | boolean | null;
}

export interface OneOfSchemaField extends SchemaBehaviorOptions {
  readonly kind: typeof SchemaKind.oneOf;
  readonly values: readonly SchemaField[];
}

export interface AnyOfSchemaField extends SchemaBehaviorOptions {
  readonly kind: typeof SchemaKind.anyOf;
  readonly values: readonly SchemaField[];
}

export interface FileSchemaField extends SchemaBehaviorOptions {
  readonly kind: typeof SchemaKind.file;
}

export interface NoContentSchemaField extends SchemaBehaviorOptions {
  readonly kind: typeof SchemaKind.noContent;
}

export type SchemaField =
  | PrimitiveSchemaField
  | CompositeSchemaField
  | RefSchemaField
  | RecordSchemaField
  | LiteralSchemaField
  | OneOfSchemaField
  | AnyOfSchemaField
  | FileSchemaField
  | NoContentSchemaField;

export type SchemaFieldMap = Readonly<Record<string, SchemaField>>;
export type PropertyDefinitionField = Exclude<SchemaField, NoContentSchemaField>;
export type PropertyDefinitionFieldMap = Readonly<Record<string, PropertyDefinitionField>>;
