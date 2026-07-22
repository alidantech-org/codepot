export const EngineIdPart = {
  version: 'version',
  resource: 'resource',

  property: 'property',
  primitive: 'primitive',
  enum: 'enum',
  composite: 'composite',

  schema: 'schema',
  entity: 'entity',
  field: 'field',
  fieldSet: 'field_set',
  model: 'model',
  dto: 'dto',
  params: 'params',

  error: 'error',

  security: 'security',
  credential: 'credential',
  principal: 'principal',
  policy: 'policy',

  route: 'route',
  operation: 'operation',
} as const;

export type EngineIdPart = (typeof EngineIdPart)[keyof typeof EngineIdPart];

export function createEngineId(...parts: Array<string | number | undefined>): string {
  return parts
    .filter((part): part is string | number => part !== undefined)
    .map((part) => String(part).trim())
    .filter(Boolean)
    .join(':');
}
