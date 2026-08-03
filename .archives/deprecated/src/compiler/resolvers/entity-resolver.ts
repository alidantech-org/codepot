// src/compiler/resolvers/entity-resolver.ts

import type { EntityAuthoringDefinition } from '@/contract/types/authoring/5.schemas-builder';

import type { EntityFieldInput, EntityFieldInputLike } from '@/contract/types/authoring/4.properties-builder';

import type { EntityDefinition } from '@/contract/types/ir/schema/entity/definition';
import type { EntityFieldDefinition } from '@/contract/types/ir/schema/entity/field/definition';

import type { CompilerContext } from '../context/compiler-context';

import { entityRef } from './ref-resolver';
import { resolveEntityField } from './field-resolver';

import { toSnakeCaseKey } from '@/utils/naming/normalize-key';

// ============================================================================
// INPUT
// ============================================================================

export interface ResolveEntityInput {
  readonly ctx: CompilerContext;
  readonly key: string;
  readonly entity: EntityAuthoringDefinition;
}

// ============================================================================
// DEFINITION ITEM
// ============================================================================

/**
 * Copies shared definition metadata from authoring into IR.
 */
function resolveDefinitionItem(input: {
  readonly description?: string;
  readonly deprecated?: boolean;
  readonly meta?: Record<string, unknown>;
}): Record<string, unknown> {
  return {
    ...(input.description !== undefined ? { description: input.description } : {}),
    ...(input.deprecated !== undefined ? { deprecated: input.deprecated } : {}),
    ...(input.meta !== undefined ? { meta: input.meta } : {}),
  };
}

// ============================================================================
// FIELD NORMALIZATION
// ============================================================================

/**
 * Unwraps a field builder into its raw authoring entity field input.
 *
 * Field helpers usually expose `{ input }`, while prebuilt authoring state may
 * already contain the raw `EntityFieldInput`.
 */
function unwrapEntityFieldInput(input: EntityFieldInputLike): EntityFieldInput {
  if ('input' in input) {
    return input.input;
  }

  return input;
}

/**
 * Checks whether a field is a relation field.
 *
 * Relation fields are intentionally skipped in this resolver because relation
 * fields are handled by `relation-resolver.ts`.
 */
function isRelationField(input: EntityFieldInput): boolean {
  return input.source.mode === 'relation';
}

// ============================================================================
// FIELDS
// ============================================================================

/**
 * Resolves normal property fields owned by an entity.
 *
 * Relation fields are skipped here and added by the relation pass later.
 */
function resolveEntityFields(
  ctx: CompilerContext,
  entityKey: string,
  fields: EntityAuthoringDefinition['fields'],
): Record<string, EntityFieldDefinition> {
  const output: Record<string, EntityFieldDefinition> = {};

  for (const [fieldKey, rawField] of Object.entries(fields)) {
    const field = unwrapEntityFieldInput(rawField);

    if (isRelationField(field)) {
      continue;
    }

    output[toSnakeCaseKey(fieldKey)] = resolveEntityField({
      ctx,
      entityKey,
      fieldKey: toSnakeCaseKey(fieldKey),
      field,
    });
  }

  return output;
}

// ============================================================================
// EXTENDS
// ============================================================================

/**
 * Resolves entity inheritance into an IR entity reference.
 */
function resolveEntityExtends(input: EntityAuthoringDefinition['extends']) {
  if (input === undefined) return undefined;

  return entityRef(toSnakeCaseKey(input.key));
}

// ============================================================================
// RESOLVE
// ============================================================================

/**
 * Converts one authoring entity definition into an IR entity definition.
 *
 * This resolver compiles:
 * - entity metadata
 * - entity inheritance
 * - normal property fields
 *
 * Relation fields are added later by the relation pass.
 */
export function resolveEntity(input: ResolveEntityInput): EntityDefinition {
  const entityKey = toSnakeCaseKey(input.key);

  return {
    ...resolveDefinitionItem(input.entity),

    ...(input.entity.abstract !== undefined ? { abstract: input.entity.abstract } : {}),

    ...(input.entity.tags !== undefined ? { tags: [...input.entity.tags] } : {}),

    ...(input.entity.extends !== undefined ? { extends: resolveEntityExtends(input.entity.extends) } : {}),

    fields: resolveEntityFields(input.ctx, entityKey, input.entity.fields),
  };
}
