import type { ComponentRef, PropertyRef } from '../refs/ref.types.js';
import type { RefWithUsageMethods } from '../refs/ref-usage.types.js';
import type { SchemaCompositionFieldValue, SchemaCompositionFieldMap } from '../schema/schema.types.js';

export type ComponentFieldValue = SchemaCompositionFieldValue;

export type ComponentFieldMap = SchemaCompositionFieldMap;

export type { SchemaCompositionFieldValue };

export type ComponentRefMap<TInput, TRef> = {
  readonly [Key in keyof TInput & string]: TRef;
};

export type SchemaComponentRefMap<TInput> = {
  readonly [Key in keyof TInput & string]: RefWithUsageMethods<ComponentRef>;
};
