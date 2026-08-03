// src/compiler/resolvers/property-resolver.ts

import type {
  EnumPropertySourceInput,
  PrimitivePropertySourceInput,
  PropertySourceInput,
} from '@/contract/types/authoring/4.properties-builder';

import type { PropertyAuthoringRef } from '@/contract/types/authoring/3.authoring-ref';

import type { Ref } from '@/contract/types/ir/ref';
import type { CompositeDefinition } from '@/contract/types/ir/properties/composite/definition';
import type { EnumDefinition } from '@/contract/types/ir/properties/enum/definition';
import type { PrimitiveDefinition } from '@/contract/types/ir/properties/primitive/definition';

import { createOwnedKey } from '../naming/owned-key';

import { entityRef, propertyCompositeRef, propertyEnumRef, propertyPrimitiveRef } from './ref-resolver';
import { toKebabCase, toSnakeCaseKey } from '@/utils/naming/normalize-key';

// ============================================================================
// RESOLVER TYPES
// ============================================================================

export const CompiledPropertyKind = {
  primitive: 'primitive',
  enum: 'enum',
  composite: 'composite',
} as const;

export type CompiledPropertyKind = (typeof CompiledPropertyKind)[keyof typeof CompiledPropertyKind];

export interface ResolvedPropertyRef {
  readonly kind: CompiledPropertyKind;
  readonly key: string;
  readonly ref: Ref;
}

export interface PromotedPropertyDefinition {
  readonly kind: CompiledPropertyKind;
  readonly key: string;
  readonly ref: Ref;
  readonly definition: PrimitiveDefinition | EnumDefinition | CompositeDefinition;
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
// VALIDATION
// ============================================================================

/**
 * Converts authoring validation keys into IR validation keys.
 *
 * Authoring stays camelCase, while IR uses normalized snake_case keys.
 */
function resolvePrimitiveValidation(validation?: PrimitivePropertySourceInput['validation']): Record<string, unknown> | undefined {
  if (validation === undefined) return undefined;

  const output: Record<string, unknown> = {};

  for (const [key, value] of Object.entries(validation)) {
    output[toSnakeCaseKey(key)] = value;
  }

  return output;
}

// ============================================================================
// PRIMITIVES
// ============================================================================

/**
 * Normalizes primitive format values from authoring to IR.
 *
 * Authoring can use camelCase helper names like `dateTime`; IR should use
 * stable kebab-case values like `date-time`.
 */
function resolvePrimitiveFormat(format: PrimitivePropertySourceInput['format']): PrimitiveDefinition['format'] {
  if (format === undefined) return undefined;

  return toKebabCase(format) as PrimitiveDefinition['format'];
}

/**
 * Converts an authoring primitive property into an IR primitive definition.
 */
export function resolvePrimitiveProperty(input: PrimitivePropertySourceInput): PrimitiveDefinition {
  return {
    ...resolveDefinitionItem(input),

    type: input.type,

    ...(input.format !== undefined ? { format: resolvePrimitiveFormat(input.format) } : {}),

    ...(input.validation !== undefined ? { validation: resolvePrimitiveValidation(input.validation) } : {}),

    ...(input.example !== undefined ? { example: input.example } : {}),
  } as PrimitiveDefinition;
}

// ============================================================================
// ENUMS
// ============================================================================

/**
 * Converts enum values from authoring map/array style into IR array style.
 */
function resolveEnumValues(values: EnumPropertySourceInput['values']): EnumDefinition['values'] {
  if (Array.isArray(values)) {
    return values.map((value) => ({
      value,
    })) as EnumDefinition['values'];
  }

  return Object.values(values).map((entry) => {
    if (typeof entry === 'string' || typeof entry === 'number') {
      return {
        value: entry,
      };
    }

    return {
      ...resolveDefinitionItem(entry),
      value: entry.value,
      ...(entry.label !== undefined ? { label: entry.label } : {}),
    };
  }) as EnumDefinition['values'];
}

/**
 * Converts an authoring enum property into an IR enum definition.
 */
export function resolveEnumProperty(input: EnumPropertySourceInput): EnumDefinition {
  return {
    ...resolveDefinitionItem(input),
    values: resolveEnumValues(input.values),
  };
}

// ============================================================================
// AUTHORING REF PARSING
// ============================================================================

/**
 * Parses a property authoring ref id.
 *
 * Expected examples:
 * - property:primitive:id
 * - property:enum:UserRole
 * - property:composite:money
 */
function parsePropertyAuthoringRef(input: PropertyAuthoringRef): ResolvedPropertyRef {
  const parts = input.id.split(':');

  if (parts.length < 3 || parts[0] !== 'property') {
    throw new Error(`Expected property authoring ref, got "${input.id}".`);
  }

  const rawKind = parts[1];
  const key = toSnakeCaseKey(parts.slice(2).join('_'));

  if (rawKind === CompiledPropertyKind.primitive) {
    return {
      kind: CompiledPropertyKind.primitive,
      key,
      ref: propertyPrimitiveRef(key),
    };
  }

  if (rawKind === CompiledPropertyKind.enum) {
    return {
      kind: CompiledPropertyKind.enum,
      key,
      ref: propertyEnumRef(key),
    };
  }

  if (rawKind === CompiledPropertyKind.composite) {
    return {
      kind: CompiledPropertyKind.composite,
      key,
      ref: propertyCompositeRef(key),
    };
  }

  throw new Error(`Unsupported property authoring ref kind "${rawKind}".`);
}

/**
 * Resolves a property authoring ref into an IR `$ref`.
 */
export function resolvePropertyRef(input: PropertyAuthoringRef): ResolvedPropertyRef {
  return parsePropertyAuthoringRef(input);
}

// ============================================================================
// INLINE PROMOTION
// ============================================================================

/**
 * Promotes an inline authoring primitive/enum property into a reusable IR
 * property definition and returns the promoted `$ref`.
 *
 * Composite inline promotion is intentionally not supported here yet because
 * nested composites need recursive ownership naming.
 */
function promoteInlinePropertyWithOwnership(input: PropertySourceInput, key: string, ownership: Ref): PromotedPropertyDefinition {
  if (input.kind === CompiledPropertyKind.primitive) {
    return {
      kind: CompiledPropertyKind.primitive,
      key,
      ref: propertyPrimitiveRef(key),
      definition: {
        ...resolvePrimitiveProperty(input),
        ownership,
      },
    };
  }

  if (input.kind === CompiledPropertyKind.enum) {
    return {
      kind: CompiledPropertyKind.enum,
      key,
      ref: propertyEnumRef(key),
      definition: {
        ...resolveEnumProperty(input),
        ownership,
      },
    };
  }

  throw new Error(`Inline property kind "${input.kind}" is not supported for promotion yet.`);
}

/**
 * Promotes an entity field inline property using entity-owned keys.
 */
export function promoteEntityInlineProperty(input: PropertySourceInput, entityKey: string, fieldKey: string): PromotedPropertyDefinition {
  return promoteInlinePropertyWithOwnership(input, createOwnedKey('entity', entityKey, fieldKey), entityRef(toSnakeCaseKey(entityKey)));
}

/**
 * Promotes a composite member inline property using composite-owned keys.
 */
export function promoteCompositeInlineProperty(
  input: PropertySourceInput,
  compositeKey: string,
  memberKey: string,
): PromotedPropertyDefinition {
  return promoteInlinePropertyWithOwnership(
    input,
    createOwnedKey('composite', compositeKey, memberKey),
    propertyCompositeRef(toSnakeCaseKey(compositeKey)),
  );
}
