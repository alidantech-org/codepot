import type { DefinitionOwner, InfoInput, NormalizedInfo } from '../core/authoring.types';
import type { ComponentRef, PropertyRef } from '../refs/ref.types';
import type { RefWithUsageMethods } from '../refs/ref-usage.types';

export type AccessAllowMap<TValue extends string = string> = Partial<Record<TValue, true>>;
export type AccessAllowSelection<TValue extends string, TMap extends Record<string, true>> = TMap & { readonly [TKey in Exclude<keyof TMap, TValue>]: never };
export interface AccessRoleSource<TValue extends string = string> { readonly source: RefWithUsageMethods<PropertyRef> | PropertyRef; readonly allow: AccessAllowMap<TValue>; }
export type AccessRoleSources = Readonly<Record<string, AccessRoleSource>>;
export interface AccessDefinitionObject { readonly context: RefWithUsageMethods<ComponentRef> | ComponentRef | null; readonly roles?: AccessRoleSources; readonly tags?: readonly string[]; readonly description?: string; readonly info?: InfoInput | NormalizedInfo; }
export interface AccessDefinitionBuilder { build(): AccessDefinitionObject; }
export type AccessDefinitionInput = AccessDefinitionObject | AccessDefinitionBuilder;
export interface NormalizedAccessDefinition extends Omit<AccessDefinitionObject, 'info'> { readonly key: string; readonly owner: DefinitionOwner; readonly info?: NormalizedInfo; }
export interface AccessRef<TKey extends string = string> { readonly key: TKey; readonly name: TKey; readonly owner: DefinitionOwner; readonly definition: NormalizedAccessDefinition & { readonly key: TKey }; }
export type AccessRefMap<TInput extends Record<string, AccessDefinitionInput>> = { readonly [TKey in keyof TInput & string]: AccessRef<TKey> };
export interface AccessRegistry<TInput extends Record<string, AccessDefinitionInput> = Record<string, AccessDefinitionInput>> { readonly owner: DefinitionOwner; readonly definitions: readonly (NormalizedAccessDefinition & { readonly key: keyof TInput & string })[]; readonly ref: AccessRefMap<TInput>; }
export interface AccessBuilder { context(context: ComponentRef | null): AccessBuilder; roles(roles: AccessRoleSources): AccessBuilder; tags(tags: readonly string[]): AccessBuilder; description(description: string): AccessBuilder; info(info: InfoInput): AccessBuilder; build(): AccessDefinitionObject; }
