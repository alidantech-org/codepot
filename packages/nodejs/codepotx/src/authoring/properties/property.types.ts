import type { z } from '../schema/z-compat';
import type { PropertyRef } from '../refs/ref.types';
import type { RefUsage, RefWithAccessAllowMethods, RefWithUsageMethods } from '../refs/ref-usage.types';
import type { PropertyDefinitionFieldMap } from '../schema/schema.types';
import { PropertyKind } from './property-kind';

export type ZodPropertyDefinitionFieldMap = Readonly<Record<string, z.ZodTypeAny>>;

export interface PropertyGroupOptions {
  readonly emitSchema?: boolean;
  readonly abstract?: boolean;
}

export interface PropertyDefinitionBase {
  readonly name: string;
  readonly fields: PropertyDefinitionFieldMap;
  readonly emitSchema?: boolean;
  readonly abstract?: boolean;
}

export interface SharedPropertyDefinition extends PropertyDefinitionBase {
  readonly kind: typeof PropertyKind.shared;
}

export interface ForRefPropertyDefinition extends PropertyDefinitionBase {
  readonly kind: typeof PropertyKind.forRef;
}

export type PropertyDefinition = SharedPropertyDefinition | ForRefPropertyDefinition;
export type PropertyRefGroup = Readonly<Record<string, RefWithUsageMethods<PropertyRef> | RefUsage<PropertyRef>>>;

export type PropertyFieldRefMap<TFields> = {
  readonly [TKey in keyof TFields & string]: PropertyRefForField<TFields[TKey]>;
};

type PropertyRefForField<TField> = TField extends z.ZodTypeAny
  ? string extends z.infer<TField>
    ? RefWithUsageMethods<PropertyRef>
    : z.infer<TField> extends string
      ? RefWithAccessAllowMethods<PropertyRef, z.infer<TField>>
      : RefWithUsageMethods<PropertyRef>
  : RefWithUsageMethods<PropertyRef>;

export type PropertyGroupRegistry<TRefs extends PropertyRefGroup = PropertyRefGroup> = {
  readonly name: string;
  readonly definitions: readonly PropertyDefinition[];
  readonly ref: TRefs;
};

export type PropertyRegistryRef = PropertyRef | PropertyRefGroup;

export interface PropertyRegistry {
  readonly name: string;
  readonly definitions: readonly PropertyDefinition[];
  readonly ref: Readonly<Record<string, PropertyRegistryRef>>;
}
