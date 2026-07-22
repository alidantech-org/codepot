export const EngineIdPart = {
  version: 'version',
  resource: 'resource',
  property: 'property',
  component: 'component',
  model: 'model',
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
