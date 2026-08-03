// src/compiler/passes/04-field-sets.ts

import type { CompilerContext } from '../context/compiler-context';

import { createFieldSetKey, resolveFieldSet, resolveGeneratedFieldSets } from '../resolvers/field-set-resolver';

import { toSnakeCaseKey } from '@/utils/naming/normalize-key';

// ============================================================================
// PASS
// ============================================================================

/**
 * Compiles generated entity field sets and field-set overrides into IR field_sets.
 *
 * Field sets are emitted as owned root schema artifacts using keys like
 * `entity.user.list_select`.
 */
export function compileFieldSets(ctx: CompilerContext): void {
  for (const [entityKey, entity] of Object.entries(ctx.authoring.schemas.entities ?? {})) {
    const compiledEntityKey = toSnakeCaseKey(entityKey);
    const generatedFieldSets = resolveGeneratedFieldSets(ctx, compiledEntityKey);

    for (const [fieldSetKey, fieldSet] of Object.entries(generatedFieldSets)) {
      ctx.ir.schemas.field_sets[fieldSetKey] = fieldSet;
    }

    for (const [fieldSetKey, override] of Object.entries(entity.fieldSetOverrides ?? {})) {
      const compiledFieldSetKey = createFieldSetKey(compiledEntityKey, fieldSetKey);

      ctx.ir.schemas.field_sets[compiledFieldSetKey] = resolveFieldSet({
        ctx,
        entity_key: compiledEntityKey,
        field_set_key: fieldSetKey,
        override,
      });
    }
  }
}
