import type { z } from 'zod';

export function isZodEnum(schema: z.ZodTypeAny): boolean {
  const def = (schema as unknown as { _def?: Record<string, unknown> })._def;
  const type = def?.type ?? def?.typeName;

  return type === 'enum' || type === 'ZodEnum';
}
