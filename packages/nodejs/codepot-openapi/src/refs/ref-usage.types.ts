import type { z } from 'zod';
import type { ComponentRef, EngineRef, ModelRef, PropertyRef } from './ref.types.js';
import type { SchemaCompositionFieldMap } from '../schema/schema.types.js';
import type { ComponentFieldMap } from '../components/component.types.js';
import type { AccessAllowSelection, AccessRoleSource } from '../access/access.types.js';
import type { RouteFieldSource, RouteSourceRef } from '../routes/route.types.js';

export type FieldSourceOrigin = 'base' | 'extension' | 'inline' | 'inherited' | 'path';

export interface FieldSourceMetadata {
  readonly origin: FieldSourceOrigin;

  readonly sourceRefId?: string;
  readonly sourceSchemaName?: string;
  readonly sourceResource?: string;

  readonly fieldKey?: string;
  readonly propertyRefId?: string;
  readonly propertyResource?: string;
  readonly propertyEntity?: string;

  readonly shared?: boolean;
}

export type ExtendWithInput = SchemaCompositionFieldMap | ModelRef | RefUsage<ModelRef>;

export type ProjectionFieldSelection<
  TFields extends Record<string, unknown>,
  TMap extends Record<string, true>,
> = TMap & {
  readonly [K in Exclude<keyof TMap, keyof TFields>]: never;
};

export interface SchemaProjection {
  readonly source: string;
  readonly rootSource?: string;
  readonly mode: 'partial' | 'pick' | 'omit';
  readonly fields?: readonly string[];
  readonly steps?: readonly SchemaProjectionStep[];
}

export interface SchemaProjectionStep {
  readonly mode: SchemaProjection['mode'];
  readonly fields?: readonly string[];
}

export type SchemaProjectionDefinition<
  TSourceName extends string,
  TFields extends Record<string, unknown>,
  TMode extends SchemaProjection['mode'],
> = {
  readonly kind: 'schema-projection-definition';
  readonly source: TSourceName;
  readonly sourceRefId: string;
  readonly mode: TMode;
  readonly fields?: readonly string[];
  readonly steps?: readonly SchemaProjectionStep[];
  readonly __fields?: TFields;
  partial(): SchemaProjectionDefinition<TSourceName, TFields, 'partial'>;
  pick<const TMap extends Record<string, true>>(
    fields: ProjectionFieldSelection<TFields, TMap>,
  ): SchemaProjectionDefinition<TSourceName, Pick<TFields, keyof TMap & keyof TFields>, 'pick'>;
  omit<const TMap extends Record<string, true>>(
    fields: ProjectionFieldSelection<TFields, TMap>,
  ): SchemaProjectionDefinition<TSourceName, Omit<TFields, keyof TMap & keyof TFields>, 'omit'>;
};

export type SchemaExtendedRefUsage<TRef extends ComponentRef, TFields extends Record<string, unknown>> = RefUsage<TRef> & {
  readonly __schemaFields?: TFields;
};

export interface RefUsageOptions {
  readonly required?: boolean;
  readonly nullable?: boolean;
  readonly array?: boolean;
  readonly extendWith?: ExtendWithInput;

  readonly composition?: {
    readonly base?: FieldSourceMetadata;
    readonly extensions?: readonly FieldSourceMetadata[];
  };

  readonly source?: RouteFieldSource;
}

export type SchemaRefWithUsageMethods<TRef extends ComponentRef, TFields extends Record<string, unknown>> = Omit<
  RefWithUsageMethods<TRef>,
  'extendWith'
> & {
  extendWith<TExtensionFields extends SchemaCompositionFieldMap>(
    fields: TExtensionFields,
  ): SchemaExtendedRefUsage<TRef, TFields & TExtensionFields>;
  partial(): SchemaProjectionDefinition<TRef['name'], TFields, 'partial'>;
  pick<const TMap extends Record<string, true>>(
    fields: ProjectionFieldSelection<TFields, TMap>,
  ): SchemaProjectionDefinition<TRef['name'], Pick<TFields, keyof TMap & keyof TFields>, 'pick'>;
  omit<const TMap extends Record<string, true>>(
    fields: ProjectionFieldSelection<TFields, TMap>,
  ): SchemaProjectionDefinition<TRef['name'], Omit<TFields, keyof TMap & keyof TFields>, 'omit'>;
};

export interface RefUsage<TRef extends EngineRef = EngineRef> {
  readonly ref: TRef;
  readonly usage: RefUsageOptions;
  optional(): RefUsage<TRef>;
  required(): RefUsage<TRef>;
  nullable(): RefUsage<TRef>;
  nonNullable(): RefUsage<TRef>;
  array(): RefUsage<TRef>;
  extendWith(fields: ExtendWithInput): RefUsage<TRef>;
  zod(): z.ZodTypeAny;
  source(source: RouteFieldSource['route'] | RouteSourceRef): RefUsage<TRef>;
}

export type RefWithUsageMethods<TRef extends EngineRef> = TRef & {
  optional(): RefUsage<TRef>;
  required(): RefUsage<TRef>;
  nullable(): RefUsage<TRef>;
  nonNullable(): RefUsage<TRef>;
  array(): RefUsage<TRef>;
  extendWith(fields: ExtendWithInput): RefUsage<TRef>;
  zod(): z.ZodTypeAny;
  source(source: RouteFieldSource['route'] | RouteSourceRef): RefUsage<TRef>;
};

export type RefWithAccessAllowMethods<TRef extends PropertyRef, TValue extends string> = RefWithUsageMethods<TRef> & {
  allow<const TAllow extends Record<string, true>>(
    allow: AccessAllowSelection<TValue, TAllow>,
  ): AccessRoleSource<TValue> & { readonly allow: TAllow };
};
