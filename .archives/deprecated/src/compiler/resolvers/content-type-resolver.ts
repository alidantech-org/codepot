// src/compiler/resolvers/content-type-resolver.ts

import { BuiltinContentTypes, ContentTypeStrategy, DefaultContentTypeKey } from '@/contract/constants';

import type { ContentDefinition } from '@/contract/types/authoring/content.types';
import type { ContentStrategy, ContentTypeDefinition } from '@/contract/types/ir/content/definition';

import { toSnakeCaseKey } from '@/utils/naming/normalize-key';

// ============================================================================
// INPUT TYPES
// ============================================================================

export type ContentTypeResolverInput = ContentDefinition;

export type ContentListResolverInput = ContentDefinition | readonly ContentDefinition[];

// ============================================================================
// DEFAULTS
// ============================================================================

/**
 * Finds a built-in content descriptor by key.
 *
 * This prevents default content from becoming `undefined`.
 */
function findBuiltinContentType(key: string): ContentDefinition {
  const contentType = BuiltinContentTypes.find((item) => item.key === key);

  if (!contentType) {
    throw new Error(`Missing built-in content type "${key}".`);
  }

  return contentType;
}

/**
 * Default JSON content descriptor shared by compiler route normalization.
 */
export const DEFAULT_JSON_CONTENT = findBuiltinContentType(DefaultContentTypeKey);

/**
 * Built-in content descriptors that should always exist in compiled IR.
 */
export const DEFAULT_CONTENT_TYPES: readonly ContentDefinition[] = BuiltinContentTypes;

// ============================================================================
// TYPE GUARDS
// ============================================================================

/**
 * Checks whether content input is a list of content descriptors.
 *
 * This custom guard is needed because `Array.isArray()` does not narrow
 * readonly arrays cleanly in this union.
 */
function isContentDefinitionList(input: ContentListResolverInput): input is readonly ContentDefinition[] {
  return Array.isArray(input);
}

// ============================================================================
// NORMALIZE
// ============================================================================

/**
 * Normalizes an authoring content key into an IR `content_types` key.
 */
export function normalizeContentTypeKey(input: ContentTypeResolverInput): string {
  return toSnakeCaseKey(input.key);
}

/**
 * Normalizes a content strategy into the IR content strategy type.
 *
 * Authoring allows custom strings, but the current IR type is stricter.
 * When the user omits strategy, we default to `custom`.
 */
function normalizeContentStrategy(strategy: string | undefined): ContentStrategy {
  return (strategy ?? ContentTypeStrategy.custom) as ContentStrategy;
}

/**
 * Normalizes optional single/multiple content descriptors into an array.
 *
 * Missing content defaults to JSON.
 */
export function normalizeContentList(input?: ContentListResolverInput): readonly ContentDefinition[] {
  if (input === undefined) return [DEFAULT_JSON_CONTENT];

  return isContentDefinitionList(input) ? input : [input];
}

/**
 * Normalizes optional single/multiple content descriptors into an array only
 * when content exists.
 *
 * This is used for no-content responses where no content type should be added.
 */
export function normalizeOptionalContentList(input?: ContentListResolverInput): readonly ContentDefinition[] | undefined {
  if (input === undefined) return undefined;

  return isContentDefinitionList(input) ? input : [input];
}

// ============================================================================
// RESOLVE
// ============================================================================

/**
 * Converts an authoring content descriptor into an IR content type definition.
 */
export function resolveContentType(input: ContentTypeResolverInput): ContentTypeDefinition {
  return {
    ...(input.description !== undefined ? { description: input.description } : {}),
    ...(input.deprecated !== undefined ? { deprecated: input.deprecated } : {}),
    ...(input.meta !== undefined ? { meta: input.meta } : {}),

    type: input.type,
    strategy: normalizeContentStrategy(input.strategy),
  };
}
