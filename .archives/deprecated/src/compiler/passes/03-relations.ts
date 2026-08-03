// src/compiler/passes/03-relations.ts

import type { EntityFieldInput, EntityFieldInputLike } from '@/contract/types/authoring/4.properties-builder';

import type { CompilerContext } from '../context/compiler-context';

import { resolveRelationField } from '../resolvers/relation-resolver';

import { toSnakeCaseKey } from '@/utils/naming/normalize-key';

// ============================================================================
// FIELD NORMALIZATION
// ============================================================================

/**
 * Unwraps a field builder into its raw authoring entity field input.
 */
function unwrapEntityFieldInput(input: EntityFieldInputLike): EntityFieldInput {
  if ('input' in input) {
    return input.input;
  }

  return input;
}

/**
 * Checks whether a field is a relation field.
 */
function isRelationField(input: EntityFieldInput): boolean {
  return input.source.mode === 'relation';
}

// ============================================================================
// PASS
// ============================================================================

/**
 * Adds relation fields to already compiled IR entities.
 *
 * This pass assumes `compileEntities` already created the entity records and
 * normal property fields.
 */
export function compileRelations(ctx: CompilerContext): void {
  for (const [entityKey, entity] of Object.entries(ctx.authoring.schemas.entities ?? {})) {
    const compiledEntityKey = toSnakeCaseKey(entityKey);
    const compiledEntity = ctx.ir.schemas.entities[compiledEntityKey];

    if (!compiledEntity) {
      throw new Error(`Entity "${compiledEntityKey}" must be compiled before relations.`);
    }

    for (const [fieldKey, rawField] of Object.entries(entity.fields)) {
      const field = unwrapEntityFieldInput(rawField);

      if (!isRelationField(field)) {
        continue;
      }

      const compiledFieldKey = toSnakeCaseKey(fieldKey);

      compiledEntity.fields[compiledFieldKey] = resolveRelationField({
        ctx,
        entityKey: compiledEntityKey,
        fieldKey: compiledFieldKey,
        field,
      });
    }
  }
}
