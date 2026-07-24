export const RefKind = {
  property: 'property',
  component: 'component',
  model: 'model',
  parameter: 'parameter',
  requestBody: 'request-body',
  response: 'response',
  route: 'route',
  operation: 'operation',
} as const;

export type RefKind = (typeof RefKind)[keyof typeof RefKind];
