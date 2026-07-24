export const OpenApiRefPattern = {
  schemas: '#/components/schemas/',
  responses: '#/components/responses/',
  parameters: '#/components/parameters/',
  requestBodies: '#/components/requestBodies/',
} as const;

export type OpenApiRefPattern = (typeof OpenApiRefPattern)[keyof typeof OpenApiRefPattern];
