import type { JsonObject } from '@/contract/index';

import type { InfoInput, NormalizedInfo, ResourceContext } from '../core/authoring.types';
import type { ComponentRef, ParameterRef, RequestBodyRef, ResponseRef } from '../refs/ref.types';
import type { RefUsage, RefWithUsageMethods, SchemaProjection, SchemaProjectionDefinition } from '../refs/ref-usage.types';
import type { SchemaField, SchemaFieldMap } from '../schema/schema.types';

export type ComponentFieldValue =
  | SchemaField
  | SchemaFieldMap
  | Readonly<Record<string, unknown>>
  | ComponentRef
  | RefUsage<ComponentRef>
  | SchemaProjectionDefinition<string, Record<string, unknown>, SchemaProjection['mode']>;
export type ComponentFieldMap = Readonly<Record<string, unknown>>;

export interface SchemaComponentDefinition {
  readonly name: string;
  readonly value: ComponentFieldValue;
  readonly required?: readonly string[];
  readonly projection?: SchemaProjection;
  readonly info?: NormalizedInfo;
}

export type SchemaComponentValue = ComponentFieldValue | { readonly schema: ComponentFieldValue; readonly info?: InfoInput };

export type SchemaComponentRefMap<TInput extends Record<string, SchemaComponentValue>> = {
  readonly [TKey in keyof TInput & string]: RefWithUsageMethods<ComponentRef>;
};

export interface SchemaComponentRegistry<TInput extends Record<string, SchemaComponentValue> = Record<string, SchemaComponentValue>> {
  readonly name: string;
  readonly definitions: SchemaComponentDefinition[];
  readonly ref: SchemaComponentRefMap<TInput>;
}

export type ParameterLocation = 'path' | 'query' | 'header' | 'cookie';

export interface ParameterComponentInput {
  readonly location: ParameterLocation;
  readonly schema: unknown;
  readonly required?: boolean;
  readonly description?: string;
}

export interface ParameterComponentDefinition extends ParameterComponentInput {
  readonly key: string;
}

export interface ParameterComponentRegistry<TInput extends Record<string, ParameterComponentInput> = Record<string, ParameterComponentInput>> {
  readonly name: string;
  readonly definitions: readonly ParameterComponentDefinition[];
  readonly ref: { readonly [TKey in keyof TInput & string]: ParameterRef };
}

export interface RequestBodyComponentInput {
  readonly schema: unknown;
  readonly required?: boolean;
  readonly description?: string;
  readonly contentType?: string | readonly string[];
}

export interface RequestBodyComponentDefinition extends RequestBodyComponentInput {
  readonly name: string;
}

export interface RequestBodyComponentRegistry<TInput extends Record<string, RequestBodyComponentInput> = Record<string, RequestBodyComponentInput>> {
  readonly name: string;
  readonly definitions: readonly RequestBodyComponentDefinition[];
  readonly ref: { readonly [TKey in keyof TInput & string]: RequestBodyRef };
}

export interface ResponseComponentInput {
  readonly schema?: unknown;
  readonly description?: string;
  readonly contentType?: string | readonly string[];
  readonly headers?: Readonly<Record<string, unknown>>;
}

export interface ResponseComponentDefinition extends ResponseComponentInput {
  readonly name: string;
}

export interface ResponseComponentRegistry<TInput extends Record<string, ResponseComponentInput> = Record<string, ResponseComponentInput>> {
  readonly name: string;
  readonly definitions: readonly ResponseComponentDefinition[];
  readonly ref: { readonly [TKey in keyof TInput & string]: ResponseRef };
}

export interface DefineComponentOptions {
  readonly name: string;
  readonly resource?: ResourceContext;
  readonly state: import('../core/authoring.types').AuthoringState;
}

export interface ComponentMetadata {
  readonly kind: string;
  readonly shared?: boolean;
  readonly resource?: { readonly name: string; readonly path: readonly string[] };
  readonly details?: JsonObject;
}
