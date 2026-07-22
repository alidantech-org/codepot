import type { JsonObject } from '@/contract/index';

import type { AuthoringState, InfoInput, NormalizedInfo } from './authoring.types';

export function createAuthoringState(): AuthoringState {
  return { schemaDefinitionsByRefId: new Map<string, unknown>() };
}

export function normalizeInfo(input: InfoInput | undefined): NormalizedInfo | undefined {
  if (input === undefined) return undefined;
  if (typeof input === 'string') return { description: input };
  if (Array.isArray(input)) return { description: input.filter(Boolean).join('\n\n') };
  const value = input as JsonObject;
  return {
    ...(typeof value.summary === 'string' ? { summary: value.summary } : {}),
    ...(typeof value.description === 'string' ? { description: value.description } : {}),
    details: value,
  };
}

export function ownerFromResource(resource?: { readonly alias: string; readonly folders: readonly string[] }):
  | { readonly global: true }
  | { readonly resource: { readonly name: string; readonly path: readonly string[] } } {
  return resource
    ? { resource: { name: resource.alias, path: [...resource.folders] } }
    : { global: true };
}
