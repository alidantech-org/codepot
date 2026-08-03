// src/compiler/passes/02-entities.ts

import type { CompilerContext } from '../context/compiler-context';

import { resolveEntity } from '../resolvers/entity-resolver';

import { toSnakeCaseKey } from '@/utils/naming/normalize-key';

// ============================================================================
// PASS
// ============================================================================

/**
 * Compiles authoring entities into IR entity schemas.
 *
 * This pass compiles only normal entity fields. Relation fields are skipped here
 * and added by `compileRelations`.
 */
export function compileEntities(ctx: CompilerContext): void {
  for (const [key, entity] of Object.entries(ctx.authoring.schemas.entities ?? {})) {
    ctx.ir.schemas.entities[toSnakeCaseKey(key)] = resolveEntity({
      ctx,
      key,
      entity,
    });
  }
}
