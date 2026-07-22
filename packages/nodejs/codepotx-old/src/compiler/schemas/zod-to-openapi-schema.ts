import { toJSONSchema, z } from 'zod';
import { fixOpenApiSchema } from './fix-openapi-schema.js';

export type ZodSchemaMode = 'input' | 'output';

export function zodToOpenApiSchema(schema: z.ZodTypeAny, mode: ZodSchemaMode = 'output'): unknown {
  const zodWithJsonSchema = z as typeof z & {
    toJSONSchema?: typeof toJSONSchema;
  };

  if (typeof zodWithJsonSchema.toJSONSchema !== 'function') {
    throw new Error('z.toJSONSchema is not available. Use Zod v4 with JSON Schema support.');
  }

  const openapiSchema = zodWithJsonSchema.toJSONSchema(schema, {
    target: 'openapi-3.1',
    io: mode,
    unrepresentable: 'any',
    cycles: 'ref',
    reused: 'inline',
  });

  return fixOpenApiSchema(openapiSchema);
}

type toJSONSchema = (
  schema: z.ZodTypeAny,
  options: {
    target: 'openapi-3.1';
    io: ZodSchemaMode;
    unrepresentable: 'any';
    cycles: 'ref';
    reused: 'inline';
  },
) => unknown;
