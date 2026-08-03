import type { EntityAuthoringRef, EntityFieldAuthoringRef } from '@/contract/types/authoring/3.authoring-ref';

import type {
  AnyEntityResult,
  EntityExtendsInput,
  EntityTargetInput,
  ResolvedEntityTargetInput,
} from '@/contract/types/authoring/4.properties-builder';

export function isAuthoringRef(value: unknown): value is {
  readonly id: string;
  readonly kind: string;
  readonly key: string;
} {
  return !!value && typeof value === 'object' && 'id' in value && 'kind' in value && 'key' in value;
}

export function isEntityResult(value: unknown): value is AnyEntityResult {
  return (
    !!value && typeof value === 'object' && 'ref' in value && 'entity' in value && typeof (value as { name?: unknown }).name === 'string'
  );
}

export function resolveEntityTarget(target: EntityTargetInput): ResolvedEntityTargetInput {
  if (typeof target === 'function') {
    return target() as ResolvedEntityTargetInput;
  }
  return target as ResolvedEntityTargetInput;
}

export function normalizeEntityTarget(target: EntityTargetInput): EntityAuthoringRef {
  const resolved = resolveEntityTarget(target);

  if (isEntityResult(resolved)) {
    return resolved.ref.entity;
  }

  return resolved;
}

export function normalizeMaybeEntityTarget<T>(value: T): T | EntityAuthoringRef {
  if (isEntityResult(value)) return value.entity;

  return value;
}
