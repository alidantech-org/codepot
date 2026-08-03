// src/compiler/resolvers/error-resolver.ts

import type { ErrorInput, ErrorsAuthoringState } from '@/contract/types/authoring/8.errors-builder';

import type { ContentDefinition } from '@/contract/types/authoring/content.types';

import type { ErrorResponseDefinition } from '@/contract/types/ir/response/errors/definition';
import type { Ref } from '@/contract/types/ir/ref';

import { contentTypeRef, dtoRef, modelRef, propertyCompositeRef, propertyEnumRef, propertyPrimitiveRef } from './ref-resolver';

import { DEFAULT_JSON_CONTENT, normalizeContentList, normalizeContentTypeKey, resolveContentType } from './content-type-resolver';

import type { CompilerContext } from '../context/compiler-context';

import { toSnakeCaseKey } from '@/utils/naming/normalize-key';

// ============================================================================
// INPUT
// ============================================================================

export interface ResolveErrorResponseInput {
  readonly ctx: CompilerContext;
  readonly key: string;
  readonly error: ErrorInput;
}

// ============================================================================
// AUTHORING REF GUARDS
// ============================================================================

/**
 * Checks whether an input value is an authoring ref-like object.
 */
function isAuthoringRef(input: unknown): input is {
  readonly id: string;
  readonly kind: string;
  readonly key: string;
} {
  return (
    input !== null &&
    typeof input === 'object' &&
    'id' in input &&
    typeof input.id === 'string' &&
    'kind' in input &&
    typeof input.kind === 'string' &&
    'key' in input &&
    typeof input.key === 'string'
  );
}

/**
 * Checks whether a value is a ref usage wrapper with a nested ref.
 */
function isUsageWrapper(input: unknown): input is {
  readonly ref: unknown;
} {
  return input !== null && typeof input === 'object' && 'ref' in input;
}

/**
 * Unwraps error schema usage into its underlying authoring ref when needed.
 */
function unwrapErrorSchema(input: ErrorInput['schema']): unknown {
  if (isUsageWrapper(input)) {
    return input.ref;
  }

  return input;
}

// ============================================================================
// DEFINITION ITEM
// ============================================================================

/**
 * Copies shared definition metadata from authoring into IR.
 */
function resolveDefinitionItem(input: {
  readonly description?: string;
  readonly deprecated?: boolean;
  readonly meta?: Record<string, unknown>;
}): Record<string, unknown> {
  return {
    ...(input.description !== undefined ? { description: input.description } : {}),
    ...(input.deprecated !== undefined ? { deprecated: input.deprecated } : {}),
    ...(input.meta !== undefined ? { meta: input.meta } : {}),
  };
}

// ============================================================================
// SCHEMA REF
// ============================================================================

/**
 * Resolves an authoring error schema ref into an IR schema/property ref.
 */
function resolveErrorSchemaRef(input: ErrorInput['schema']): Ref {
  const value = unwrapErrorSchema(input);

  if (!isAuthoringRef(value)) {
    throw new Error('Error schema must be an authoring ref or usage wrapper.');
  }

  if (value.kind === 'schema.dto') {
    return dtoRef(toSnakeCaseKey(value.key));
  }

  if (value.kind === 'schema.model') {
    return modelRef(toSnakeCaseKey(value.key));
  }

  if (value.kind === 'property.primitive') {
    return propertyPrimitiveRef(toSnakeCaseKey(value.key));
  }

  if (value.kind === 'property.enum') {
    return propertyEnumRef(toSnakeCaseKey(value.key));
  }

  if (value.kind === 'property.composite') {
    return propertyCompositeRef(toSnakeCaseKey(value.key));
  }

  throw new Error(`Unsupported error schema ref kind "${value.kind}".`);
}

// ============================================================================
// CONTENT TYPES
// ============================================================================

/**
 * Registers one error content type and returns a ref to it.
 */
function registerErrorContentType(ctx: CompilerContext, content: ContentDefinition): Ref {
  const key = normalizeContentTypeKey(content);

  ctx.ir.content_types[key] = resolveContentType(content);

  return contentTypeRef(key);
}

/**
 * Resolves error content into the primary required IR content type.
 *
 * ErrorResponseDefinition currently requires `content_type`, so missing authoring
 * content defaults to JSON.
 */
function resolvePrimaryErrorContentType(ctx: CompilerContext, content: ErrorInput['content']): Ref {
  const [first] = normalizeContentList(content);

  return registerErrorContentType(ctx, first ?? DEFAULT_JSON_CONTENT);
}

/**
 * Resolves all error content descriptors into IR content type refs.
 *
 * This is useful if the IR keeps `content_types` as an optional extra field.
 */
function resolveErrorContentTypes(ctx: CompilerContext, content: ErrorInput['content']): readonly Ref[] {
  return normalizeContentList(content).map((item) => registerErrorContentType(ctx, item));
}

// ============================================================================
// HEADERS
// ============================================================================

/**
 * Resolves optional error headers into IR refs.
 */
function resolveErrorHeaders(headers: ErrorInput['headers']): ErrorResponseDefinition['headers'] {
  if (headers === undefined) return undefined;

  const output: NonNullable<ErrorResponseDefinition['headers']> = {};

  for (const [key, schema] of Object.entries(headers)) {
    output[toSnakeCaseKey(key)] = resolveErrorSchemaRef(schema);
  }

  return output;
}

// ============================================================================
// RESOLVE
// ============================================================================

/**
 * Converts one authoring error definition into an IR error response definition.
 */
export function resolveErrorResponse(input: ResolveErrorResponseInput): ErrorResponseDefinition {
  const { ctx, error } = input;

  return {
    ...resolveDefinitionItem(error),

    ...(error.intent !== undefined ? { intent: error.intent } : {}),

    status: error.status,
    schema: resolveErrorSchemaRef(error.schema),
    content_type: resolvePrimaryErrorContentType(ctx, error.content),

    ...(error.content !== undefined ? { content_types: resolveErrorContentTypes(ctx, error.content) } : {}),

    ...(error.headers !== undefined ? { headers: resolveErrorHeaders(error.headers) } : {}),
  };
}

// ============================================================================
// STATE
// ============================================================================

/**
 * Removes undefined entries from a partial authoring error map.
 */
export function getErrorsState(state: Partial<ErrorsAuthoringState> | undefined): ErrorsAuthoringState {
  const output: ErrorsAuthoringState = {};

  for (const [key, error] of Object.entries(state ?? {})) {
    if (error !== undefined) {
      output[key] = error;
    }
  }

  return output;
}
