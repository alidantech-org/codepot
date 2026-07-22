// src/contract/types/core/8.errors-builder.ts

import type { DtoAuthoringRef, ErrorAuthoringRef, MaybeUsage } from './3.authoring-ref';

import type { DefinitionItem } from './4.properties-builder';

import type { ContentDefinition, ContentInput, ContentHelper } from './content.types';

// ============================================================================
// SHARED ERROR INPUTS
// ============================================================================

export type ErrorSchemaInput = MaybeUsage<DtoAuthoringRef>;

// ============================================================================
// ERRORS
// ============================================================================

export interface ErrorInput extends DefinitionItem {
  readonly status: number;
  readonly schema: ErrorSchemaInput;
  readonly content?: readonly ContentDefinition[];
  readonly headers?: Record<string, ErrorSchemaInput>;
  readonly intent?: string;
}

export type ErrorInputMap = Record<string, ErrorInput>;

export interface ErrorsResult<TInput extends ErrorInputMap> {
  readonly errors: TInput;

  readonly ref: {
    readonly [K in keyof TInput & string]: ErrorAuthoringRef;
  };
}

// ============================================================================
// ERRORS AUTHORING STATE (mutable, not compiled IR)
// ============================================================================

export type ErrorsAuthoringState = Record<string, ErrorInput>;

// ============================================================================
// ERRORS BUILDER
// ============================================================================

export interface ErrorsBuilder {
  readonly state: Partial<ErrorsAuthoringState>;

  readonly content: ContentHelper;

  error(status: number, schema: ErrorSchemaInput, contentOrOptions?: ContentInput | Omit<ErrorInput, 'status' | 'schema'>): ErrorInput;

  define<TInput extends ErrorInputMap>(input: TInput): ErrorsResult<TInput>;

  snapshot(): Partial<ErrorsAuthoringState>;
}
