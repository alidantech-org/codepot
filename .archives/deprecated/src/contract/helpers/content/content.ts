// src/contract/helpers/content/content.ts

import { BuiltinContentTypes, ContentMimeType, ContentTypeKey, ContentTypeStrategy } from '@/contract/constants';

import type { ContentDefinition, ContentInput } from '@/contract/types/authoring/content.types';

// ============================================================================
// INTERNAL
// ============================================================================

type ContentOptions = Omit<ContentDefinition, 'key' | 'type' | 'strategy'>;

/**
 * Creates a content descriptor used by authoring.
 *
 * The compiler later registers this descriptor under IR `content_types`
 * and replaces route content with `$ref` values.
 */
function defineContent(key: string, type: string, strategy: string, options: ContentOptions = {}): ContentDefinition {
  return {
    ...options,
    key,
    type,
    strategy,
  };
}

/**
 * Finds a built-in content descriptor by key.
 */
function builtinContent(key: Exclude<ContentTypeKey, 'custom'>, options: ContentOptions = {}): ContentDefinition {
  const builtin = BuiltinContentTypes.find((item) => item.key === key);

  if (!builtin) {
    throw new Error(`Missing built-in content type "${key}".`);
  }

  return defineContent(builtin.key, builtin.type, builtin.strategy, options);
}

// ============================================================================
// CONTENT HELPER
// ============================================================================

export const content = {
  json(options: ContentOptions = {}) {
    return builtinContent(ContentTypeKey.json, options);
  },

  xml(options: ContentOptions = {}) {
    return builtinContent(ContentTypeKey.xml, options);
  },

  yaml(options: ContentOptions = {}) {
    return builtinContent(ContentTypeKey.yaml, options);
  },

  html(options: ContentOptions = {}) {
    return builtinContent(ContentTypeKey.html, options);
  },

  csv(options: ContentOptions = {}) {
    return builtinContent(ContentTypeKey.csv, options);
  },

  text(options: ContentOptions = {}) {
    return builtinContent(ContentTypeKey.text, options);
  },

  binary(options: ContentOptions = {}) {
    return builtinContent(ContentTypeKey.binary, options);
  },

  stream(options: ContentOptions = {}) {
    return builtinContent(ContentTypeKey.stream, options);
  },

  multipart(options: ContentOptions = {}) {
    return builtinContent(ContentTypeKey.multipart, options);
  },

  form(options: ContentOptions = {}) {
    return builtinContent(ContentTypeKey.form, options);
  },

  graphql(options: ContentOptions = {}) {
    return builtinContent(ContentTypeKey.graphql, options);
  },

  protobuf(options: ContentOptions = {}) {
    return builtinContent(ContentTypeKey.protobuf, options);
  },

  msgpack(options: ContentOptions = {}) {
    return builtinContent(ContentTypeKey.msgpack, options);
  },

  custom(key: string, type: string, strategy: string = ContentTypeStrategy.custom, options: ContentOptions = {}) {
    return defineContent(key, type, strategy, options);
  },

  types(...types: ContentDefinition[]): readonly ContentDefinition[] {
    return types;
  },
};

export type { ContentDefinition, ContentInput };

export { ContentMimeType, ContentTypeKey, ContentTypeStrategy };
