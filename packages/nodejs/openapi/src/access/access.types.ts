import type { ComponentRef, PropertyRef } from '../refs/ref.types.js';
import type { RefWithUsageMethods } from '../refs/ref-usage.types.js';
import type { XCodegenResourceMeta } from '../codegen/codegen-extension.types.js';
import type { InfoInput, NormalizedInfo } from '../info/info.types.js';

export type AccessAllowMap<TValue extends string = string> = Partial<Record<TValue, true>>;

export type AccessAllowSelection<
  TValue extends string,
  TMap extends Record<string, true>,
> = TMap & {
  readonly [K in Exclude<keyof TMap, TValue>]: never;
};

export interface AccessRoleSource<TValue extends string = string> {
  readonly source: RefWithUsageMethods<PropertyRef> | PropertyRef;
  readonly allow: AccessAllowMap<TValue>;
}

export type AccessRoleSources = Record<string, AccessRoleSource>;

export interface AccessOwnerGlobal {
  readonly global: true;
}

export interface AccessOwnerResource {
  readonly resource: XCodegenResourceMeta;
}

export type AccessOwner = AccessOwnerGlobal | AccessOwnerResource;

export interface AccessDefinitionObject {
  readonly context: RefWithUsageMethods<ComponentRef> | ComponentRef | null;
  readonly roles?: AccessRoleSources;
  readonly tags?: readonly string[];
  readonly description?: string;
  readonly info?: InfoInput | NormalizedInfo;
}

export interface AccessDefinitionBuilder {
  build(): AccessDefinitionObject;
}

export type AccessDefinitionInput = AccessDefinitionObject | AccessDefinitionBuilder;

export type AccessDefinition = AccessDefinitionObject;

export type NormalizedAccessDefinition = AccessDefinitionObject & {
  readonly key: string;
  readonly owner: AccessOwner;
};

export interface AccessRef<TKey extends string = string> {
  readonly key: TKey;
  readonly name: TKey;
  readonly owner: AccessOwner;
  readonly definition: NormalizedAccessDefinition & { readonly key: TKey };
}

export type AccessRefMap<TInput extends Record<string, AccessDefinitionInput>> = {
  readonly [Key in keyof TInput & string]: AccessRef<Key>;
};

export interface AccessRegistry<TInput extends Record<string, AccessDefinitionInput> = Record<string, AccessDefinitionInput>> {
  readonly owner: AccessOwner;
  readonly definitions: readonly (NormalizedAccessDefinition & { readonly key: keyof TInput & string })[];
  readonly ref: AccessRefMap<TInput>;
}

export type AccessAllowedValues<T> = T extends { readonly _output: infer TOutput }
  ? Extract<TOutput, string>
  : string;
