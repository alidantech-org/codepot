import type { AuthoringRef, AuthoringRefKind, RefUsage } from '@/contract/types/authoring/3.authoring-ref';

interface DebugAuthoringRef {
  readonly id: string;
  readonly kind: string;
  readonly key: string;
}

interface DebugRefUsage {
  readonly ref: DebugAuthoringRef;
  readonly usage: unknown;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return !!value && typeof value === 'object' && !Array.isArray(value);
}

function isAuthoringRef(value: unknown): value is AuthoringRef<unknown, AuthoringRefKind> {
  return isRecord(value) && typeof value.id === 'string' && typeof value.kind === 'string' && typeof value.key === 'string';
}

function isRefUsage(value: unknown): value is RefUsage<unknown, AuthoringRefKind> {
  return isRecord(value) && isAuthoringRef(value.ref) && isRecord(value.usage);
}

function toDebugRef(ref: AuthoringRef<unknown, AuthoringRefKind>): DebugAuthoringRef {
  return {
    id: ref.id,
    kind: ref.kind,
    key: ref.key,
  };
}

function toDebugUsage(usage: RefUsage<unknown, AuthoringRefKind>): DebugRefUsage {
  return {
    ref: toDebugRef(usage.ref),
    usage: toDebugAuthoringJson(usage.usage),
  };
}

export function toDebugAuthoringJson<TValue>(value: TValue): TValue {
  if (isRefUsage(value)) {
    return toDebugUsage(value) as TValue;
  }

  if (isAuthoringRef(value)) {
    return toDebugRef(value) as TValue;
  }

  if (!value || typeof value !== 'object') {
    return value;
  }

  if (Array.isArray(value)) {
    return value.map((item) => toDebugAuthoringJson(item)) as TValue;
  }

  const output: Record<string, unknown> = {};

  for (const [key, child] of Object.entries(value)) {
    if (typeof child === 'function') continue;

    const normalized = toDebugAuthoringJson(child);

    if (normalized !== undefined) {
      output[key] = normalized;
    }
  }

  return output as TValue;
}
