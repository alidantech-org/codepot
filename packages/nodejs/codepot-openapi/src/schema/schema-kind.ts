export const SchemaKind = {
  primitive: 'primitive',
  composite: 'composite',
  ref: 'ref',
  record: 'record',
  literal: 'literal',
  oneOf: 'oneOf',
  anyOf: 'anyOf',
  file: 'file',
  noContent: 'noContent',
} as const;

export type SchemaKind = (typeof SchemaKind)[keyof typeof SchemaKind];
