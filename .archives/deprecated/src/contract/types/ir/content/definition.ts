// src/contract/types/ir/content/definition.ts

import type { DefinitionItem } from '../definition';

export const ContentStrategy = {
  json: 'json',
  xml: 'xml',
  yaml: 'yaml',
  html: 'html',
  csv: 'csv',
  multipart: 'multipart',
  form: 'form',
  text: 'text',
  binary: 'binary',
  stream: 'stream',
  custom: 'custom',
} as const;

export type ContentStrategy = (typeof ContentStrategy)[keyof typeof ContentStrategy];

export interface ContentTypeDefinition extends DefinitionItem {
  type: string;
  strategy: ContentStrategy;

  binary?: boolean;
  structured?: boolean;
}
