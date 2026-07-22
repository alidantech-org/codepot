// src/compiler/passes/00-content-types.ts

import type { CompilerContext } from '../context/compiler-context';

import {
  DEFAULT_CONTENT_TYPES,
  normalizeContentTypeKey,
  resolveContentType,
  type ContentTypeResolverInput,
} from '../resolvers/content-type-resolver';

// ============================================================================
// REGISTER
// ============================================================================

/**
 * Registers one content type in the compiled IR.
 *
 * Content types are stored once under `ir.content_types`; routes and responses
 * later reference them by `$ref`.
 */
function registerContentType(ctx: CompilerContext, input: ContentTypeResolverInput): void {
  const key = normalizeContentTypeKey(input);

  ctx.ir.content_types[key] = resolveContentType(input);
}

// ============================================================================
// PASS
// ============================================================================

/**
 * Registers all built-in content types in the compiled IR.
 *
 * Custom content types can be discovered and added later by route/error passes.
 */
export function compileContentTypes(ctx: CompilerContext): void {
  for (const contentType of DEFAULT_CONTENT_TYPES) {
    registerContentType(ctx, contentType);
  }
}
