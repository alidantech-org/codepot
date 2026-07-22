import type { ComponentFieldMap } from '../component.types.js';
import type { ComponentRef } from '../../refs/ref.types.js';
import type { EngineRef } from '../../refs/ref.types.js';
import type {
  RefWithUsageMethods,
  SchemaExtendedRefUsage,
  SchemaProjection,
  SchemaProjectionDefinition,
  SchemaRefWithUsageMethods,
} from '../../refs/ref-usage.types.js';
import type { RefUsage } from '../../refs/ref-usage.types.js';
import type { CodegenMetadata } from '../../codegen/codegen-extension.types.js';

export type SchemaComponentValue =
  | ComponentFieldMap
  | EngineRef
  | SchemaExtendedRefUsage<ComponentRef, Record<string, unknown>>
  | RefUsage<EngineRef>
  | RefUsage<ComponentRef>
  | SchemaProjectionDefinition<string, Record<string, unknown>, SchemaProjection['mode']>;

export interface SchemaComponentDefinition {
  readonly name: string;
  readonly value: SchemaComponentValue;
  readonly meta?: CodegenMetadata;
  readonly projection?: SchemaProjection;
  readonly required?: readonly string[];
}

export type InferSchemaComponentFields<TValue> = TValue extends ComponentFieldMap
  ? TValue
  : TValue extends SchemaProjectionDefinition<string, infer TFields, SchemaProjection['mode']>
    ? TFields
  : TValue extends SchemaExtendedRefUsage<ComponentRef, infer TFields>
    ? TFields
  : TValue extends { readonly __schemaFields?: infer TFields }
    ? TFields extends Record<string, unknown>
      ? TFields
      : Record<string, unknown>
  : TValue extends RefUsage<infer TRef>
    ? TRef extends ComponentRef
      ? TValue['usage'] extends { extendWith?: infer TExtendWith }
        ? TExtendWith extends ComponentFieldMap
          ? TExtendWith
          : Record<string, unknown>
        : Record<string, unknown>
      : Record<string, unknown>
    : Record<string, unknown>;

export type SchemaComponentRefs<TInput extends Record<string, unknown>> = {
  readonly [Key in keyof TInput & string]: SchemaRefWithUsageMethods<ComponentRef & { readonly name: Key }, InferSchemaComponentFields<TInput[Key]>>;
};

export interface SchemaComponentRegistry<TInput extends Record<string, unknown> = Record<string, SchemaComponentValue>> {
  readonly name: string;
  readonly definitions: SchemaComponentDefinition[];
  readonly ref: SchemaComponentRefs<TInput>;
}
