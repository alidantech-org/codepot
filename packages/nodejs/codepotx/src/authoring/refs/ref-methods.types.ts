import type { z } from '../schema/z-compat';

export interface RefMethodOptions {
  readonly toZod?: (value: unknown) => z.ZodTypeAny;
}
