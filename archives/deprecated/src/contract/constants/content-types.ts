// src/contract/constants/content-types.ts

import { valueObject } from './values';

// ============================================================================
// CONTENT TYPE KEYS
// ============================================================================

export const ContentTypeKeyValues = [
  'json',
  'xml',
  'yaml',
  'html',
  'csv',
  'text',
  'binary',
  'stream',
  'multipart',
  'form',
  'graphql',
  'protobuf',
  'msgpack',
  'custom',
] as const;

export const ContentTypeKey = valueObject(ContentTypeKeyValues);

export type ContentTypeKey = (typeof ContentTypeKeyValues)[number];

// ============================================================================
// CONTENT TYPE STRATEGIES
// ============================================================================

export const ContentTypeStrategyValues = ContentTypeKeyValues;

export const ContentTypeStrategy = valueObject(ContentTypeStrategyValues);

export type ContentTypeStrategy = (typeof ContentTypeStrategyValues)[number];

// ============================================================================
// MIME TYPES
// ============================================================================

export const ContentMimeType = {
  json: 'application/json',
  xml: 'application/xml',
  yaml: 'application/yaml',
  html: 'text/html',
  csv: 'text/csv',
  text: 'text/plain',
  binary: 'application/octet-stream',
  stream: 'application/octet-stream',
  multipart: 'multipart/form-data',
  form: 'application/x-www-form-urlencoded',
  graphql: 'application/graphql',
  protobuf: 'application/x-protobuf',
  msgpack: 'application/msgpack',
} as const;

// ============================================================================
// DEFAULT CONTENT DESCRIPTORS
// ============================================================================

export interface BuiltinContentTypeDefinition {
  readonly key: Exclude<ContentTypeKey, 'custom'>;
  readonly type: string;
  readonly strategy: Exclude<ContentTypeStrategy, 'custom'>;
}

export const BuiltinContentTypes = [
  {
    key: ContentTypeKey.json,
    type: ContentMimeType.json,
    strategy: ContentTypeStrategy.json,
  },
  {
    key: ContentTypeKey.xml,
    type: ContentMimeType.xml,
    strategy: ContentTypeStrategy.xml,
  },
  {
    key: ContentTypeKey.yaml,
    type: ContentMimeType.yaml,
    strategy: ContentTypeStrategy.yaml,
  },
  {
    key: ContentTypeKey.html,
    type: ContentMimeType.html,
    strategy: ContentTypeStrategy.html,
  },
  {
    key: ContentTypeKey.csv,
    type: ContentMimeType.csv,
    strategy: ContentTypeStrategy.csv,
  },
  {
    key: ContentTypeKey.text,
    type: ContentMimeType.text,
    strategy: ContentTypeStrategy.text,
  },
  {
    key: ContentTypeKey.binary,
    type: ContentMimeType.binary,
    strategy: ContentTypeStrategy.binary,
  },
  {
    key: ContentTypeKey.stream,
    type: ContentMimeType.stream,
    strategy: ContentTypeStrategy.stream,
  },
  {
    key: ContentTypeKey.multipart,
    type: ContentMimeType.multipart,
    strategy: ContentTypeStrategy.multipart,
  },
  {
    key: ContentTypeKey.form,
    type: ContentMimeType.form,
    strategy: ContentTypeStrategy.form,
  },
  {
    key: ContentTypeKey.graphql,
    type: ContentMimeType.graphql,
    strategy: ContentTypeStrategy.graphql,
  },
  {
    key: ContentTypeKey.protobuf,
    type: ContentMimeType.protobuf,
    strategy: ContentTypeStrategy.protobuf,
  },
  {
    key: ContentTypeKey.msgpack,
    type: ContentMimeType.msgpack,
    strategy: ContentTypeStrategy.msgpack,
  },
] as const satisfies readonly BuiltinContentTypeDefinition[];

export const DefaultContentTypeKey = ContentTypeKey.json;
