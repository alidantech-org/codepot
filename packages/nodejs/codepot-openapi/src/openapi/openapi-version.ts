export const OpenApiVersion = {
  v3_0_3: '3.0.3',
  v3_1_0: '3.1.0',
} as const;

export type OpenApiVersion = (typeof OpenApiVersion)[keyof typeof OpenApiVersion];
