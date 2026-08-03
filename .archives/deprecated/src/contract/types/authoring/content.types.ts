// src/contract/types/authoring/content.types.ts

import type { DefinitionItem } from './4.properties-builder';
import type { ContentTypeKey, ContentTypeStrategy } from '@/contract/constants';

export interface ContentDefinition extends DefinitionItem {
  readonly key: ContentTypeKey | string;
  readonly type: string;
  readonly strategy?: ContentTypeStrategy | string;
}

export type ContentInput = ContentDefinition | readonly ContentDefinition[];

// ============================================================================
// CONTENT HELPER
// ============================================================================

export interface ContentHelper {
  json(options?: DefinitionItem): ContentDefinition;

  xml(options?: DefinitionItem): ContentDefinition;

  yaml(options?: DefinitionItem): ContentDefinition;

  html(options?: DefinitionItem): ContentDefinition;

  csv(options?: DefinitionItem): ContentDefinition;

  text(options?: DefinitionItem): ContentDefinition;

  binary(options?: DefinitionItem): ContentDefinition;

  stream(options?: DefinitionItem): ContentDefinition;

  multipart(options?: DefinitionItem): ContentDefinition;

  form(options?: DefinitionItem): ContentDefinition;

  graphql(options?: DefinitionItem): ContentDefinition;

  protobuf(options?: DefinitionItem): ContentDefinition;

  msgpack(options?: DefinitionItem): ContentDefinition;

  custom(key: string, type: string, strategy?: string): ContentDefinition;

  types(...types: ContentDefinition[]): readonly ContentDefinition[];
}
