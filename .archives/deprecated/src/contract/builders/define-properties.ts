// src/contract/builders/define-properties.ts

import type {
  CompositeAuthoringRef,
  EnumAuthoringRef,
  PrimitiveAuthoringRef,
  PropertyAuthoringRef,
} from '@/contract/types/authoring/3.authoring-ref';

import type {
  CompositePropertiesResult,
  CompositePropertySourceInput,
  CompositePropertySourceMap,
  CompositePropertyValueInput,
  EnumPropertiesResult,
  EnumPropertySourceInput,
  EnumPropertySourceMap,
  NormalizedCompositePropertySourceInput,
  NormalizedPropertyMemberInput,
  PrimitivePropertiesResult,
  PrimitivePropertySourceInput,
  PrimitivePropertySourceMap,
  PropertiesAuthoringState,
  PropertiesBuilder,
  PropertyRefsResult,
  PropertySourceInput,
  PropertySourceInputLike,
  PropertySourceMap,
} from '@/contract/types/authoring/4.properties-builder';

import { PropertySlotSourceMode } from '@/contract/types/authoring/4.properties-builder';

import { createInlinePropertyPromotionHint, unwrapPropertySourceInput } from '@/contract/helpers/properties/inline-property';

import { compositeRef, enumRef, primitiveRef, propertyRefFromSource } from '@/contract/helpers/refs/authoring-ref-builder';

// ============================================================================
// OPTIONS
// ============================================================================

export interface DefinePropertiesOptions {
  readonly scope: 'version' | 'resource';
  readonly resourceKey?: string;
  readonly state: Partial<PropertiesAuthoringState>;
}

// ============================================================================
// STATE HELPERS
// ============================================================================

function ensurePropertiesState(state: Partial<PropertiesAuthoringState>): PropertiesAuthoringState {
  state.primitives ??= {};
  state.enums ??= {};
  state.composites ??= {};

  return state as PropertiesAuthoringState;
}

function isPropertySourceBuilder(value: PropertySourceInputLike): value is { readonly input: PropertySourceInput } {
  return !!value && typeof value === 'object' && 'input' in value;
}

function isPropertyRef(value: unknown): value is PropertyAuthoringRef {
  return (
    !!value &&
    typeof value === 'object' &&
    'id' in value &&
    'kind' in value &&
    'key' in value &&
    typeof (value as { kind: unknown }).kind === 'string' &&
    (value as { kind: string }).kind.startsWith('property.')
  );
}

function normalizeCompositeMember(input: {
  readonly compositeKey: string;
  readonly fieldKey: string;
  readonly value: CompositePropertyValueInput;
}): NormalizedPropertyMemberInput {
  if (isPropertyRef(input.value)) {
    return {
      source: {
        mode: PropertySlotSourceMode.ref,
        ref: input.value,
      },
    };
  }

  return {
    source: {
      mode: PropertySlotSourceMode.inline,
      property: unwrapPropertySourceInput(input.value),
      promote: createInlinePropertyPromotionHint({
        ownerKind: 'composite',
        ownerKey: input.compositeKey,
        fieldKey: input.fieldKey,
      }),
    },
  };
}

function normalizeCompositeSource(
  key: string,
  source: CompositePropertySourceInput | NormalizedCompositePropertySourceInput,
): NormalizedCompositePropertySourceInput {
  return {
    ...source,
    properties: Object.fromEntries(
      Object.entries(source.properties).map(([fieldKey, value]) => [
        fieldKey,
        normalizeCompositeMember({
          compositeKey: key,
          fieldKey,
          value,
        }),
      ]),
    ) as NormalizedCompositePropertySourceInput['properties'],
  };
}

function toPropertySourceInput(key: string, value: PropertySourceInputLike): PropertySourceInput {
  const source = isPropertySourceBuilder(value) ? value.input : value;

  if (source.kind === 'composite') {
    return normalizeCompositeSource(key, source);
  }

  return source;
}

function normalizePropertySources<TFields extends PropertySourceMap>(fields: TFields): Record<keyof TFields & string, PropertySourceInput> {
  const normalized = {} as Record<keyof TFields & string, PropertySourceInput>;

  for (const [key, value] of Object.entries(fields) as [keyof TFields & string, TFields[keyof TFields & string]][]) {
    normalized[key] = toPropertySourceInput(key, value);
  }

  return normalized;
}

function writePrimitiveSource(state: PropertiesAuthoringState, key: string, source: PrimitivePropertySourceInput): void {
  state.primitives[key] = source;
}

function writeEnumSource(state: PropertiesAuthoringState, key: string, source: EnumPropertySourceInput): void {
  state.enums[key] = source;
}

function writeCompositeSource(
  state: PropertiesAuthoringState,
  key: string,
  source: CompositePropertySourceInput | NormalizedCompositePropertySourceInput,
): void {
  state.composites[key] = source as CompositePropertySourceInput;
}

function writePropertySource(state: PropertiesAuthoringState, key: string, source: PropertySourceInput): void {
  if (source.kind === 'primitive') {
    writePrimitiveSource(state, key, source);
    return;
  }

  if (source.kind === 'enum') {
    writeEnumSource(state, key, source);
    return;
  }

  if (source.kind === 'composite') {
    writeCompositeSource(state, key, source);
  }
}

function writePropertySources<TFields extends PropertySourceMap>(
  state: PropertiesAuthoringState,
  fields: TFields,
): Record<keyof TFields & string, PropertySourceInput> {
  const normalized = normalizePropertySources(fields);

  for (const [key, source] of Object.entries(normalized) as [keyof TFields & string, PropertySourceInput][]) {
    writePropertySource(state, key, source);
  }

  return normalized;
}

function createPropertyRefs<TFields extends PropertySourceMap>(
  normalizedFields: Record<keyof TFields & string, PropertySourceInput>,
): Record<keyof TFields & string, PropertyAuthoringRef> {
  const refs = {} as Record<keyof TFields & string, PropertyAuthoringRef>;

  for (const [key, value] of Object.entries(normalizedFields) as [keyof TFields & string, PropertySourceInput][]) {
    refs[key] = propertyRefFromSource(key, value);
  }

  return refs;
}

function createPrimitiveRefs<TFields extends PrimitivePropertySourceMap>(fields: TFields): PrimitivePropertiesResult<TFields>['ref'] {
  const refs: Record<string, PrimitiveAuthoringRef> = {};

  for (const key of Object.keys(fields) as Array<keyof TFields & string>) {
    refs[key] = primitiveRef(key);
  }

  return refs as PrimitivePropertiesResult<TFields>['ref'];
}

function createEnumRefs<TFields extends EnumPropertySourceMap>(fields: TFields): EnumPropertiesResult<TFields>['ref'] {
  const refs: Record<string, EnumAuthoringRef> = {};

  for (const key of Object.keys(fields) as Array<keyof TFields & string>) {
    refs[key] = enumRef(key);
  }

  return refs as EnumPropertiesResult<TFields>['ref'];
}

function createCompositeRefs<TFields extends CompositePropertySourceMap>(fields: TFields): CompositePropertiesResult<TFields>['ref'] {
  const refs: Record<string, CompositeAuthoringRef> = {};

  for (const key of Object.keys(fields) as Array<keyof TFields & string>) {
    refs[key] = compositeRef(key);
  }

  return refs as CompositePropertiesResult<TFields>['ref'];
}

function writePropertyGroup<TFields extends PropertySourceMap>(
  state: Partial<PropertiesAuthoringState>,
  fields: TFields,
): PropertyRefsResult<TFields> {
  const propertiesState = ensurePropertiesState(state);
  const normalizedFields = writePropertySources(propertiesState, fields);

  return {
    fields,
    ref: createPropertyRefs(normalizedFields) as PropertyRefsResult<TFields>['ref'],
  };
}

// ============================================================================
// DEFINE PROPERTIES
// ============================================================================

export function defineProperties(options: DefinePropertiesOptions): PropertiesBuilder {
  const builder: PropertiesBuilder = {
    get state() {
      return options.state;
    },

    primitives<TFields extends PrimitivePropertySourceMap>(fields: TFields): PrimitivePropertiesResult<TFields> {
      writePropertyGroup(options.state, fields);
      return {
        fields,
        ref: createPrimitiveRefs(fields),
      };
    },

    enums<TFields extends EnumPropertySourceMap>(fields: TFields): EnumPropertiesResult<TFields> {
      writePropertyGroup(options.state, fields);
      return {
        fields,
        ref: createEnumRefs(fields),
      };
    },

    composites<TFields extends CompositePropertySourceMap>(fields: TFields): CompositePropertiesResult<TFields> {
      writePropertyGroup(options.state, fields);
      return {
        fields,
        ref: createCompositeRefs(fields),
      };
    },

    refs<TFields extends PropertySourceMap>(fields: TFields): PropertyRefsResult<TFields> {
      return writePropertyGroup(options.state, fields);
    },

    snapshot() {
      return options.state;
    },
  };

  return builder;
}
