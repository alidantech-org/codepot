export const ParameterLocation = {
  path: 'path',
  query: 'query',
  header: 'header',
  cookie: 'cookie',
} as const;

export type ParameterLocation = (typeof ParameterLocation)[keyof typeof ParameterLocation];
