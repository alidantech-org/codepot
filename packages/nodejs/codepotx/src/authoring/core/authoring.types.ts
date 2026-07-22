import type { JsonObject } from '@/contract/index';

export type InfoInput = string | readonly string[] | JsonObject;

export interface NormalizedInfo {
  readonly summary?: string;
  readonly description?: string;
  readonly details?: JsonObject;
}

export interface ResourceContext {
  readonly name: string;
  readonly route: string;
  readonly tag: string;
  readonly tags: readonly string[];
  readonly folders: readonly string[];
  readonly alias: string;
  readonly ui?: JsonObject;
  readonly access?: unknown;
  readonly info?: NormalizedInfo;
}

export interface DefinitionOwnerGlobal {
  readonly global: true;
}

export interface DefinitionOwnerResource {
  readonly resource: {
    readonly name: string;
    readonly path: readonly string[];
  };
}

export type DefinitionOwner = DefinitionOwnerGlobal | DefinitionOwnerResource;

export interface AuthoringState {
  readonly schemaDefinitionsByRefId: Map<string, unknown>;
}
