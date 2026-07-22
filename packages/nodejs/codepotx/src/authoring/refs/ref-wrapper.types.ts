import type { z } from '../schema/z-compat';
import type { EngineRef } from './ref.types';

export interface ArrayRef<TRef extends EngineRef = EngineRef> {
  readonly kind: 'array-ref';
  readonly ref: TRef;
  zod(): z.ZodTypeAny;
}

export interface ExtendedRef<TRef extends EngineRef = EngineRef> {
  readonly kind: 'extended-ref';
  readonly ref: TRef;
  readonly fields: Readonly<Record<string, unknown>>;
  zod(): z.ZodTypeAny;
}
