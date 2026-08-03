// src/compiler/resolvers/field-resolver.ts

import type {
  EntityFieldInput,
  EntityFieldOptions,
  PropertySlotInlineSource,
  PropertySlotRefSource,
  PropertySourceBuilder,
  PropertySourceInput,
} from '@/contract/types/authoring/4.properties-builder';

import type { PropertyAuthoringRef } from '@/contract/types/authoring/3.authoring-ref';

import type { RefProperty } from '@/contract/types/ir/properties/definition';
import type { Ref } from '@/contract/types/ir/ref';

import type {
  ArrayDefinition,
  EntityFieldDefinition,
  EntityFieldOptionsDefinition,
  EntityPropertyFieldDefinition,
  QueryOperator,
} from '@/contract/types/ir/schema/entity/field/definition';

import type { CompilerContext } from '../context/compiler-context';

import {
  CompiledPropertyKind,
  promoteEntityInlineProperty,
  resolvePropertyRef,
  type PromotedPropertyDefinition,
} from './property-resolver';

import { toSnakeCaseKey } from '@/utils/naming/normalize-key';

// ============================================================================
// INPUT
// ============================================================================

export interface ResolveEntityFieldInput {
  readonly ctx: CompilerContext;
  readonly entityKey: string;
  readonly fieldKey: string;
  readonly field: EntityFieldInput;
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
// TYPE GUARDS
// ============================================================================

/**
 * Checks whether an authoring ref points to a property.
 */
function isPropertyAuthoringRef(input: unknown): input is PropertyAuthoringRef {
  if (input === null || typeof input !== 'object') return false;

  const value = input as Partial<PropertyAuthoringRef>;

  return (
    typeof value.id === 'string' && typeof value.kind === 'string' && value.kind.startsWith('property.') && typeof value.key === 'string'
  );
}

/**
 * Checks whether a field source is a property ref source.
 *
 * Authoring `mode: "ref"` can also be used by model refs, so this guard
 * narrows to the property-ref-only source shape.
 */
function isPropertySlotRefSource(input: EntityFieldInput['source']): input is PropertySlotRefSource {
  return input.mode === 'ref' && isPropertyAuthoringRef(input.ref);
}

/**
 * Checks whether a value is a property source builder.
 */
function isPropertySourceBuilder(input: unknown): input is PropertySourceBuilder<PropertySourceInput> {
  return input !== null && typeof input === 'object' && 'input' in input;
}

/**
 * Checks whether a value is a raw property source.
 */
function isPropertySourceInput(input: unknown): input is PropertySourceInput {
  return input !== null && typeof input === 'object' && 'kind' in input;
}

// ============================================================================
// ARRAY
// ============================================================================

/**
 * Converts authoring array options into IR array options.
 */
function resolveArrayOptions(input: EntityFieldOptions['array']): true | ArrayDefinition | undefined {
  if (input === undefined || input === false) return undefined;
  if (input === true) return true;

  return {
    ...(input.minItems !== undefined ? { min_items: input.minItems } : {}),
    ...(input.maxItems !== undefined ? { max_items: input.maxItems } : {}),
    ...(input.uniqueItems !== undefined ? { unique_items: input.uniqueItems } : {}),
  };
}

// ============================================================================
// CAPABILITY
// ============================================================================

/**
 * Converts authoring query operators into IR query operators.
 */
function resolveQueryOperators(operators: readonly string[] | undefined): QueryOperator[] | undefined {
  if (operators === undefined) return undefined;

  return operators.map((operator) => toSnakeCaseKey(operator) as QueryOperator);
}

// ============================================================================
// FIELD OPTIONS
// ============================================================================

/**
 * Converts authoring field options into IR field options.
 *
 * Authoring uses camelCase. IR uses snake_case where needed.
 */
function resolveFieldOptions(options: EntityFieldOptions | undefined): EntityFieldOptionsDefinition {
  if (options === undefined) return {};

  return {
    ...resolveDefinitionItem(options),

    ...(options.required !== undefined ? { required: options.required } : {}),
    ...(options.nullable !== undefined ? { nullable: options.nullable } : {}),
    ...(options.default !== undefined ? { default: options.default } : {}),

    ...(options.array !== undefined ? { array: resolveArrayOptions(options.array) } : {}),

    ...(options.capability !== undefined
      ? {
          capability: {
            ...resolveDefinitionItem(options.capability),
            ...(options.capability.filter !== undefined ? { filter: options.capability.filter } : {}),
            ...(options.capability.sort !== undefined ? { sort: options.capability.sort } : {}),
            ...(options.capability.select !== undefined ? { select: options.capability.select } : {}),
            ...(options.capability.operators !== undefined ? { operators: resolveQueryOperators(options.capability.operators) } : {}),
          },
        }
      : {}),

    ...(options.visibility !== undefined
      ? {
          visibility: {
            ...resolveDefinitionItem(options.visibility),
            ...(options.visibility.read !== undefined ? { read: options.visibility.read } : {}),
            ...(options.visibility.write !== undefined ? { write: options.visibility.write } : {}),
            ...(options.visibility.sensitive !== undefined ? { sensitive: options.visibility.sensitive } : {}),
          },
        }
      : {}),

    ...(options.lifecycle !== undefined
      ? {
          lifecycle: {
            ...resolveDefinitionItem(options.lifecycle),
            ...(options.lifecycle.create !== undefined ? { create: options.lifecycle.create } : {}),
            ...(options.lifecycle.update !== undefined ? { update: options.lifecycle.update } : {}),
            ...(options.lifecycle.immutable !== undefined ? { immutable: options.lifecycle.immutable } : {}),
            ...(options.lifecycle.generated !== undefined ? { generated: options.lifecycle.generated } : {}),
            ...(options.lifecycle.readOnly !== undefined ? { read_only: options.lifecycle.readOnly } : {}),
          },
        }
      : {}),

    ...(options.persistence !== undefined
      ? {
          persistence: {
            ...resolveDefinitionItem(options.persistence),
            mode: options.persistence.mode,
            ...(options.persistence.generated !== undefined ? { generated: options.persistence.generated } : {}),
            ...(options.persistence.immutable !== undefined ? { immutable: options.persistence.immutable } : {}),
          },
        }
      : {}),
  };
}

// ============================================================================
// PROMOTION
// ============================================================================

/**
 * Registers a promoted inline property from an entity field.
 */
function registerPromotedProperty(ctx: CompilerContext, promoted: PromotedPropertyDefinition): void {
  if (promoted.kind === CompiledPropertyKind.primitive) {
    ctx.ir.properties.primitives[promoted.key] = promoted.definition as never;
    return;
  }

  if (promoted.kind === CompiledPropertyKind.enum) {
    ctx.ir.properties.enums[promoted.key] = promoted.definition as never;
    return;
  }

  if (promoted.kind === CompiledPropertyKind.composite) {
    ctx.ir.properties.composites[promoted.key] = promoted.definition as never;
  }
}

// ============================================================================
// SOURCE
// ============================================================================

/**
 * Resolves a normal ref-backed property field into an IR `$ref`.
 */
function resolveRefFieldSource(source: PropertySlotRefSource): Ref<RefProperty> {
  if (!isPropertyAuthoringRef(source.ref)) {
    throw new Error('Entity property field source must reference a property.');
  }

  return resolvePropertyRef(source.ref).ref as Ref<RefProperty>;
}

/**
 * Resolves an inline property field into an IR `$ref`.
 *
 * The inline property is promoted into the reusable IR property registry first.
 */
function resolveInlineFieldSource(
  ctx: CompilerContext,
  entityKey: string,
  fieldKey: string,
  source: PropertySlotInlineSource,
): Ref<RefProperty> {
  if (!source.property) {
    throw new Error(`Inline field "${entityKey}.${fieldKey}" is missing property source.`);
  }

  const rawSource = isPropertySourceBuilder(source.property) ? source.property.input : source.property;

  if (!isPropertySourceInput(rawSource)) {
    throw new Error(`Inline field "${entityKey}.${fieldKey}" must use a property source.`);
  }

  const promoted = promoteEntityInlineProperty(rawSource, entityKey, fieldKey);

  registerPromotedProperty(ctx, promoted);

  return promoted.ref as Ref<RefProperty>;
}

/**
 * Creates an IR property field from a resolved property ref and field options.
 */
function createPropertyField(ref: Ref<RefProperty>, options: EntityFieldOptions | undefined): EntityPropertyFieldDefinition {
  return {
    ...ref,
    ...resolveFieldOptions(options),
  };
}

// ============================================================================
// RESOLVE
// ============================================================================

/**
 * Converts one authoring entity field into an IR entity field.
 *
 * This resolver supports property ref fields and inline property fields.
 * Relation fields are handled later by `relation-resolver.ts`.
 */
export function resolveEntityField(input: ResolveEntityFieldInput): EntityFieldDefinition {
  const { ctx, entityKey, fieldKey, field } = input;

  if (field.source.mode === 'ref') {
    if (!isPropertySlotRefSource(field.source)) {
      throw new Error(`Field "${entityKey}.${fieldKey}" uses a non-property ref. Model refs are not valid entity field types.`);
    }

    return createPropertyField(resolveRefFieldSource(field.source), field.options);
  }

  if (field.source.mode === 'inline') {
    return createPropertyField(resolveInlineFieldSource(ctx, entityKey, fieldKey, field.source), field.options);
  }

  throw new Error(`Field "${entityKey}.${fieldKey}" is not a property field. Relation fields are resolved separately.`);
}
