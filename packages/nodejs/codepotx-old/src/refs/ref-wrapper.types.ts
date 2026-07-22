import type { z } from 'zod';
import type { ComponentFieldMap } from '../components/component.types.js';
import type { EngineRef } from './ref.types.js';

export interface ArrayRef<TRef extends EngineRef = EngineRef> {
  readonly kind: 'array-ref';
  readonly ref: TRef;
  zod(): z.ZodTypeAny;
}

export interface ExtendedRef<TRef extends EngineRef = EngineRef> {
  readonly kind: 'extended-ref';
  readonly ref: TRef;
  readonly fields: ComponentFieldMap;
  zod(): z.ZodTypeAny;
}
