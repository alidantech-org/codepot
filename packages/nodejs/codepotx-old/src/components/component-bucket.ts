export const ComponentBucket = {
  schemas: 'schemas',
  parameters: 'parameters',
  requestBodies: 'requestBodies',
  responses: 'responses',
} as const;

export type ComponentBucket = (typeof ComponentBucket)[keyof typeof ComponentBucket];
