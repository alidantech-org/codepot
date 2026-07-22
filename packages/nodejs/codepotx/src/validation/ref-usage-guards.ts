import type { EngineRef } from '../refs/ref.types.js';
import type { RefUsage, ExtendWithInput } from '../refs/ref-usage.types.js';
import { isEngineRef } from './ref-guards.js';

export function isRefUsage(value: unknown): value is RefUsage<EngineRef> {
  return !!value && typeof value === 'object' && 'ref' in value && 'usage' in value && isEngineRef(value.ref);
}

export function getRefRequired(value: unknown): boolean | undefined {
  return isRefUsage(value) ? value.usage.required : undefined;
}

export function getRefNullable(value: unknown): boolean | undefined {
  return isRefUsage(value) ? value.usage.nullable : undefined;
}

export function getRefArray(value: unknown): boolean | undefined {
  return isRefUsage(value) ? value.usage.array : undefined;
}

export function getRefExtendWith(value: unknown): ExtendWithInput | undefined {
  return isRefUsage(value) ? value.usage.extendWith : undefined;
}
