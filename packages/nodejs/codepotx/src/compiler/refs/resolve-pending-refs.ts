import { OpenApiRefPattern } from '../../openapi/ref-patterns.js';
import type { CompilerContext } from '../compiler-context.js';
import type { RefResolver } from './ref-resolver.types.js';

const PendingPrefix = '#pending/';

export function resolvePendingRefs(
  value: unknown,
  resolver: RefResolver,
  context?: CompilerContext,
  options?: { logSummary?: boolean },
): unknown {
  return resolvePendingRefsInternal(value, resolver, '$', context);
}

function resolvePendingRefsInternal(value: unknown, resolver: RefResolver, path: string, context?: CompilerContext): unknown {
  if (Array.isArray(value)) {
    return value.map((item, index) => resolvePendingRefsInternal(item, resolver, `${path}[${index}]`, context));
  }

  if (!isPlainObject(value)) return value;

  if (typeof value.$ref === 'string' && value.$ref.startsWith(PendingPrefix)) {
    const resolved = resolvePendingRef(value.$ref, resolver, path, context);
    const { $ref, ...siblings } = value;
    const resolvedSiblings = Object.fromEntries(
      Object.entries(siblings).map(([key, child]) => [key, resolvePendingRefsInternal(child, resolver, `${path}.${key}`, context)]),
    );

    return {
      ...resolved,
      ...resolvedSiblings,
    };
  }

  return Object.fromEntries(
    Object.entries(value).map(([key, child]) => [key, resolvePendingRefsInternal(child, resolver, `${path}.${key}`, context)]),
  );
}

function resolvePendingRef(pendingRef: string, resolver: RefResolver, path: string, context?: CompilerContext): Record<string, string> {
  const refId = pendingRef.slice(PendingPrefix.length);
  const schemaName = resolver.schemas.get(refId);

  if (!schemaName) {
    throw new Error(`Unable to resolve pending ref at ${path}: ${refId}`);
  }

  const resolvedRef = {
    $ref: `${OpenApiRefPattern.schemas}${schemaName}`,
  };

  return resolvedRef;
}

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return !!value && typeof value === 'object' && !Array.isArray(value);
}
