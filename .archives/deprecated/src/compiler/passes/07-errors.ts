// src/compiler/passes/07-errors.ts

import type { CompilerContext } from '../context/compiler-context';

import { createOwnedKey } from '../naming/owned-key';
import { getErrorsState, resolveErrorResponse } from '../resolvers/error-resolver';
import { resourceRef } from '../resolvers/ref-resolver';

import { toSnakeCaseKey } from '@/utils/naming/normalize-key';

// ============================================================================
// GLOBAL ERRORS
// ============================================================================

/**
 * Compiles version-level/global errors into IR responses.errors.
 */
function compileGlobalErrors(ctx: CompilerContext): void {
  const errors = getErrorsState(ctx.authoring.errors);

  for (const [key, error] of Object.entries(errors)) {
    ctx.ir.responses.errors[toSnakeCaseKey(key)] = resolveErrorResponse({
      ctx,
      key,
      error,
    });
  }
}

// ============================================================================
// RESOURCE ERRORS
// ============================================================================

/**
 * Creates the promoted root key for a resource-scoped error.
 *
 * Format:
 * resource.resource_key.error_key
 */
function createResourceErrorKey(resourceKey: string, errorKey: string): string {
  return createOwnedKey('resource', resourceKey, errorKey);
}

/**
 * Compiles resource-scoped errors into the same top-level IR responses.errors
 * registry.
 *
 * Resource errors do not remain nested under resources in IR.
 */
function compileResourceErrors(ctx: CompilerContext): void {
  for (const [resourceKey, resource] of Object.entries(ctx.authoring.resources ?? {})) {
    const errors = getErrorsState(resource.errors);

    for (const [errorKey, error] of Object.entries(errors)) {
      const compiledKey = createResourceErrorKey(resourceKey, errorKey);

      ctx.ir.responses.errors[compiledKey] = {
        ...resolveErrorResponse({
          ctx,
          key: compiledKey,
          error,
        }),
        ownership: resourceRef(toSnakeCaseKey(resourceKey)),
      };
    }
  }
}

// ============================================================================
// PASS
// ============================================================================

/**
 * Compiles all authoring errors into top-level IR responses.errors.
 */
export function compileErrors(ctx: CompilerContext): void {
  compileGlobalErrors(ctx);
  compileResourceErrors(ctx);
}
