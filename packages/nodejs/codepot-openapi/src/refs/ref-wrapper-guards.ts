import type { ArrayRef, ExtendedRef } from './ref-wrapper.types.js';

export function isArrayRef(value: unknown): value is ArrayRef {
  return !!value && typeof value === 'object' && 'kind' in value && value.kind === 'array-ref';
}

export function isExtendedRef(value: unknown): value is ExtendedRef {
  return !!value && typeof value === 'object' && 'kind' in value && value.kind === 'extended-ref';
}
