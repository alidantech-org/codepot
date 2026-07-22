// src/contract/helpers/errors/error.ts

import type { ErrorInput as ErrorDefinition, ErrorSchemaInput } from '@/contract/types/authoring/8.errors-builder';
import type { ContentDefinition } from '@/contract/types/authoring/content.types';

// ============================================================================
// CONTENT NORMALIZATION
// ============================================================================

function normalizeContent(value?: readonly ContentDefinition[]): readonly ContentDefinition[] | undefined {
  if (value === undefined) return undefined;

  return value;
}

function isContentDefinition(value: unknown): value is ContentDefinition {
  return !!value && typeof value === 'object' && 'type' in value && typeof (value as { type: unknown }).type === 'string';
}

function isContentDefinitionList(value: unknown): value is readonly ContentDefinition[] {
  return isContentDefinition(value) || (Array.isArray(value) && value.every(isContentDefinition));
}

// ============================================================================
// ERROR HELPER
// ============================================================================

export function error(
  status: number,
  schema: ErrorSchemaInput,
  contentOrOptions?: readonly ContentDefinition[] | Omit<ErrorDefinition, 'status' | 'schema'>,
): ErrorDefinition {
  if (contentOrOptions === undefined) {
    return {
      status,
      schema,
    };
  }

  if (isContentDefinitionList(contentOrOptions)) {
    return {
      status,
      schema,
      content: normalizeContent(contentOrOptions),
    };
  }

  return {
    ...contentOrOptions,
    status,
    schema,
    content: normalizeContent(contentOrOptions.content),
  };
}
