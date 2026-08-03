// src/compiler/passes/01-properties.ts

import type { PropertyAuthoringRef } from '@/contract/types/authoring/3.authoring-ref';
import type {
  CompositePropertySourceInput,
  CompositePropertyValueInput,
  EnumPropertySourceInput,
  InlinePropertyMemberInput,
  PrimitivePropertySourceInput,
  PropertyRefMemberInput,
  PropertySourceBuilder,
  PropertySourceInput,
} from '@/contract/types/authoring/4.properties-builder';

import type { Ref } from '@/contract/types/ir/ref';

import type { CompilerContext } from '../context/compiler-context';

import {
  CompiledPropertyKind,
  promoteCompositeInlineProperty,
  resolveEnumProperty,
  resolvePrimitiveProperty,
  resolvePropertyRef,
  type PromotedPropertyDefinition,
} from '../resolvers/property-resolver';

import { toSnakeCaseKey } from '@/utils/naming/normalize-key';

// ============================================================================
// SOURCE NORMALIZATION
// ============================================================================

/**
 * Normalizes property helper builders into raw property source inputs.
 *
 * Authoring helpers usually return `{ input }`; compiler passes should resolve
 * that wrapper before calling lower-level property resolvers.
 */
function unwrapPropertySource(input: PropertySourceInput | PropertySourceBuilder<PropertySourceInput>): PropertySourceInput {
  if ('input' in input) {
    return input.input;
  }

  return input;
}

/**
 * Checks whether a composite member is a property source builder wrapper.
 */
function isPropertySourceBuilder(input: CompositePropertyValueInput): input is PropertySourceBuilder<PropertySourceInput> {
  return input !== null && typeof input === 'object' && 'input' in input;
}

/**
 * Checks whether a composite member is a real authoring property ref.
 *
 * We require `id`, `kind`, and `key` because raw property source objects may
 * accidentally contain an `id`, but they are not refs.
 */
function isPropertyAuthoringRef(input: CompositePropertyValueInput): input is PropertyAuthoringRef {
  return (
    input !== null &&
    typeof input === 'object' &&
    'id' in input &&
    typeof input.id === 'string' &&
    'kind' in input &&
    typeof input.kind === 'string' &&
    'key' in input &&
    typeof input.key === 'string'
  );
}

/**
 * Checks whether a value is a raw property source input.
 */
function isPropertySourceInput(input: CompositePropertyValueInput): input is PropertySourceInput {
  return input !== null && typeof input === 'object' && 'kind' in input;
}

/**
 * Checks whether a composite member is a normalized ref member.
 */
function isNormalizedRefMember(input: unknown): input is PropertyRefMemberInput {
  return (
    input !== null &&
    typeof input === 'object' &&
    'source' in input &&
    input.source !== null &&
    typeof input.source === 'object' &&
    'mode' in input.source &&
    input.source.mode === 'ref' &&
    'ref' in input.source
  );
}

/**
 * Checks whether a composite member is a normalized inline member.
 */
function isNormalizedInlineMember(input: unknown): input is InlinePropertyMemberInput {
  return (
    input !== null &&
    typeof input === 'object' &&
    'source' in input &&
    input.source !== null &&
    typeof input.source === 'object' &&
    'mode' in input.source &&
    input.source.mode === 'inline' &&
    'property' in input.source
  );
}

// ============================================================================
// PROMOTION REGISTRATION
// ============================================================================

/**
 * Registers a promoted inline property in the proper IR property bucket.
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
// COMPOSITES
// ============================================================================

/**
 * Resolves one composite member into an IR property ref.
 *
 * Direct refs are converted to `$ref`. Inline property definitions are promoted
 * into reusable IR properties first, then the member points to that `$ref`.
 */
function resolveCompositeMember(ctx: CompilerContext, compositeKey: string, memberKey: string, input: CompositePropertyValueInput): Ref {
  if (isPropertyAuthoringRef(input)) {
    return resolvePropertyRef(input).ref;
  }

  if (isNormalizedRefMember(input)) {
    return resolvePropertyRef(input.source.ref as PropertyAuthoringRef).ref;
  }

  if (isNormalizedInlineMember(input)) {
    const source = unwrapPropertySource(input.source.property);
    const promoted = promoteCompositeInlineProperty(source, compositeKey, memberKey);

    registerPromotedProperty(ctx, promoted);

    return promoted.ref;
  }

  if (isPropertySourceBuilder(input)) {
    const source = unwrapPropertySource(input);
    const promoted = promoteCompositeInlineProperty(source, compositeKey, memberKey);

    registerPromotedProperty(ctx, promoted);

    return promoted.ref;
  }

  if (isPropertySourceInput(input)) {
    const promoted = promoteCompositeInlineProperty(input, compositeKey, memberKey);

    registerPromotedProperty(ctx, promoted);

    return promoted.ref;
  }

  throw new Error(`Unable to resolve composite member "${compositeKey}.${memberKey}".`);
}

/**
 * Converts an authoring composite property into an IR composite definition.
 */
function resolveCompositeProperty(ctx: CompilerContext, key: string, input: CompositePropertySourceInput) {
  const compositeKey = toSnakeCaseKey(key);
  const properties: Record<string, Ref> = {};

  for (const [memberKey, memberInput] of Object.entries(input.properties)) {
    properties[toSnakeCaseKey(memberKey)] = resolveCompositeMember(ctx, compositeKey, memberKey, memberInput);
  }

  return {
    ...(input.description !== undefined ? { description: input.description } : {}),
    ...(input.deprecated !== undefined ? { deprecated: input.deprecated } : {}),
    ...(input.meta !== undefined ? { meta: input.meta } : {}),
    ...(input.extends !== undefined ? { extends: resolvePropertyRef(input.extends).ref } : {}),
    properties,
  };
}

// ============================================================================
// PASS
// ============================================================================

/**
 * Compiles authoring properties into IR properties.
 *
 * This pass owns:
 * - primitive property definitions
 * - enum property definitions
 * - composite property definitions
 * - inline property promotion inside composites
 */
export function compileProperties(ctx: CompilerContext): void {
  const properties = ctx.authoring.properties;

  for (const [key, input] of Object.entries(properties.primitives ?? {})) {
    ctx.ir.properties.primitives[toSnakeCaseKey(key)] = resolvePrimitiveProperty(
      unwrapPropertySource(input) as PrimitivePropertySourceInput,
    );
  }

  for (const [key, input] of Object.entries(properties.enums ?? {})) {
    ctx.ir.properties.enums[toSnakeCaseKey(key)] = resolveEnumProperty(unwrapPropertySource(input) as EnumPropertySourceInput);
  }

  for (const [key, input] of Object.entries(properties.composites ?? {})) {
    ctx.ir.properties.composites[toSnakeCaseKey(key)] = resolveCompositeProperty(
      ctx,
      key,
      unwrapPropertySource(input) as CompositePropertySourceInput,
    );
  }
}
