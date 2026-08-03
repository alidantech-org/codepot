// src/compiler/validators/ref-validator.ts

import type { CodepotDefinition } from '@/contract/types/ir/definition';

// ============================================================================
// TYPES
// ============================================================================

export interface RefValidationIssue {
  readonly path: string;
  readonly ref: string;
  readonly message: string;
}

// ============================================================================
// REF DISCOVERY
// ============================================================================

/**
 * Checks whether a value is an IR ref object.
 */
function isRefObject(value: unknown): value is { readonly $ref: string } {
  return value !== null && typeof value === 'object' && '$ref' in value && typeof value.$ref === 'string';
}

/**
 * Recursively collects all `$ref` values from a JSON-like object.
 */
function collectRefs(value: unknown, path: string, output: RefValidationIssue[]): void {
  if (isRefObject(value)) {
    output.push({
      path,
      ref: value.$ref,
      message: 'unvalidated',
    });
  }

  if (Array.isArray(value)) {
    value.forEach((item, index) => {
      collectRefs(item, `${path}[${index}]`, output);
    });

    return;
  }

  if (value !== null && typeof value === 'object') {
    for (const [key, child] of Object.entries(value)) {
      collectRefs(child, `${path}.${key}`, output);
    }
  }
}

// ============================================================================
// REF RESOLUTION
// ============================================================================

/**
 * Resolves a local JSON pointer ref against the IR object.
 */
function resolveLocalRef(ir: CodepotDefinition, ref: string): unknown {
  if (!ref.startsWith('#/')) {
    return undefined;
  }

  const parts = ref
    .slice(2)
    .split('/')
    .map((part) => part.replace(/~1/g, '/').replace(/~0/g, '~'));

  let current: unknown = ir;

  for (const part of parts) {
    if (current === null || typeof current !== 'object' || !(part in current)) {
      return undefined;
    }

    current = (current as Record<string, unknown>)[part];
  }

  return current;
}

// ============================================================================
// VALIDATE
// ============================================================================

/**
 * Returns all broken refs in a compiled IR object.
 */
export function validateIrRefs(ir: CodepotDefinition): readonly RefValidationIssue[] {
  const refs: RefValidationIssue[] = [];
  const issues: RefValidationIssue[] = [];

  collectRefs(ir, '$', refs);

  for (const item of refs) {
    const target = resolveLocalRef(ir, item.ref);

    if (target === undefined) {
      issues.push({
        path: item.path,
        ref: item.ref,
        message: `Broken IR ref "${item.ref}" at "${item.path}".`,
      });
    }
  }

  return issues;
}

/**
 * Throws if the compiled IR contains broken refs.
 */
export function assertValidIrRefs(ir: CodepotDefinition): void {
  const issues = validateIrRefs(ir);

  if (issues.length === 0) return;

  throw new Error(issues.map((issue) => issue.message).join('\n'));
}
