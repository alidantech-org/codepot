// src/compiler/passes/04-models.ts

import { EntityModelVariantValues } from '@/contract/constants';

import type {
  EntityModelOverrideFactory,
  EntityModelOverrideInput,
  EntityModelVariant,
} from '@/contract/types/authoring/4.properties-builder';

import type { EntityAuthoringDefinition } from '@/contract/types/authoring/5.schemas-builder';

import type { CompilerContext } from '../context/compiler-context';

import { createEntityModelKey, resolveModel } from '../resolvers/model-resolver';

// ============================================================================
// OVERRIDES
// ============================================================================

/**
 * Resolves a model override value.
 *
 * Builder callback overrides should already be normalized by authoring, but this
 * keeps the compiler safe if raw factories remain.
 */
function resolveModelOverride(
  override: EntityModelOverrideInput<any> | EntityModelOverrideFactory<any> | undefined,
): EntityModelOverrideInput<any> | undefined {
  if (override === undefined) return undefined;

  if (typeof override === 'function') {
    throw new Error('Model override factories must be normalized before compilation.');
  }

  return override;
}

/**
 * Gets the override for one model variant.
 */
function getModelOverride(entity: EntityAuthoringDefinition, variant: EntityModelVariant): EntityModelOverrideInput<any> | undefined {
  return resolveModelOverride(entity.modelOverrides?.[variant]);
}

// ============================================================================
// PASS
// ============================================================================

/**
 * Compiles entity model variants into top-level IR schemas.models.
 *
 * Models are not nested under entities in IR. Each model gets a stable owned key like:
 * - entity.user.user_read
 * - entity.user.user_create
 * - entity.user.user_public_list
 */
export function compileModels(ctx: CompilerContext): void {
  for (const [entityKey, entity] of Object.entries(ctx.authoring.schemas.entities ?? {})) {
    for (const variant of EntityModelVariantValues) {
      const modelKey = createEntityModelKey(entityKey, variant);

      ctx.ir.schemas.models[modelKey] = resolveModel({
        ctx,
        entityKey,
        variant,
        entity,
        override: getModelOverride(entity, variant),
      });
    }
  }
}
