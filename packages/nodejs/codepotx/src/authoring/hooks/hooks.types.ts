import type { DefinitionOwner, InfoInput, NormalizedInfo } from '../core/authoring.types';
export type RuntimeHookPhase = 'before' | 'beforeValidate' | 'afterValidate' | 'beforeSuccess' | 'afterSuccess' | 'afterError' | string;
export interface RuntimeHookDefinition { readonly phase: RuntimeHookPhase; readonly transport?: { readonly inbound?: Readonly<Record<string, boolean>>; readonly outbound?: Readonly<Record<string, boolean>> }; readonly description?: string; readonly info?: InfoInput; }
export interface NormalizedRuntimeHookDefinition extends Omit<RuntimeHookDefinition, 'info'> { readonly key: string; readonly owner: DefinitionOwner; readonly info?: NormalizedInfo; }
export interface RuntimeHookRef<TKey extends string = string> { readonly key: TKey; readonly name: TKey; readonly definition: NormalizedRuntimeHookDefinition & { readonly key: TKey }; }
export interface RuntimeHookRegistry<TInput extends Record<string, RuntimeHookDefinition> = Record<string, RuntimeHookDefinition>> { readonly owner: DefinitionOwner; readonly definitions: readonly NormalizedRuntimeHookDefinition[]; readonly ref: { readonly [TKey in keyof TInput & string]: RuntimeHookRef<TKey> }; }
export interface RuntimeRouteConfig { readonly transport?: RuntimeHookDefinition['transport']; readonly hooks?: Readonly<Record<string, RuntimeHookRef>>; }
