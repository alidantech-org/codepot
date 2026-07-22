import type { ExtendWithInput } from '../../refs/ref-usage.types.js';
import type { SchemaCompositionFieldMap } from '../../schema/schema.types.js';
import type { ModelRef, ComponentRef, PropertyRef } from '../../refs/ref.types.js';
import type { FieldSourceMetadata } from '../../refs/ref-usage.types.js';
import { RefKind } from '../../refs/ref-kind.js';
import { isRefUsage } from '../../validation/ref-usage-guards.js';
import { getSourceMetadataFromRef } from '../../refs/ref-source-metadata.js';

export interface NormalizedExtendWithForQuery {
  readonly fields: SchemaCompositionFieldMap;
  readonly sourceModel?: ModelRef;
}

export interface NormalizedExtendWithWithSource {
  readonly fields: SchemaCompositionFieldMap;
  readonly source?: FieldSourceMetadata;
}

export function normalizeExtendWithInput(input: ExtendWithInput | undefined): SchemaCompositionFieldMap | undefined {
  if (!input) return undefined;

  if (isModelRef(input)) {
    return input.fields;
  }

  if (isRefUsage(input)) {
    if (isModelRef(input.ref)) {
      return input.ref.fields;
    }

    throw new Error('extendWith() RefUsage must target a ModelRef.');
  }

  if (isSchemaCompositionFieldMap(input)) {
    return input;
  }

  // Reject ComponentRef, PropertyRef, ArrayRef, ExtendedRef
  if (isComponentRef(input)) {
    throw new Error('extendWith() does not support ComponentRef. Use a field map, ModelRef, or RefUsage<ModelRef>.');
  }

  if (isPropertyRef(input)) {
    throw new Error('extendWith() does not support PropertyRef. Use a field map, ModelRef, or RefUsage<ModelRef>.');
  }

  if (isArrayRef(input)) {
    throw new Error('extendWith() does not support ArrayRef. Use a field map, ModelRef, or RefUsage<ModelRef>.');
  }

  if (isExtendedRef(input)) {
    throw new Error('extendWith() does not support ExtendedRef. Use a field map, ModelRef, or RefUsage<ModelRef>.');
  }

  throw new Error('extendWith() only supports a field map, ModelRef, or RefUsage<ModelRef>.');
}

export function normalizeExtendWithForQueryCollection(input: ExtendWithInput | undefined): NormalizedExtendWithForQuery | undefined {
  if (!input) return undefined;

  if (isModelRef(input)) {
    return { fields: input.fields, sourceModel: input };
  }

  if (isRefUsage(input)) {
    if (isModelRef(input.ref)) {
      return { fields: input.ref.fields, sourceModel: input.ref };
    }

    throw new Error('extendWith() RefUsage must target a ModelRef.');
  }

  if (isSchemaCompositionFieldMap(input)) {
    return { fields: input };
  }

  // Reject ComponentRef, PropertyRef, ArrayRef, ExtendedRef
  if (isComponentRef(input)) {
    throw new Error('extendWith() does not support ComponentRef. Use a field map, ModelRef, or RefUsage<ModelRef>.');
  }

  if (isPropertyRef(input)) {
    throw new Error('extendWith() does not support PropertyRef. Use a field map, ModelRef, or RefUsage<ModelRef>.');
  }

  if (isArrayRef(input)) {
    throw new Error('extendWith() does not support ArrayRef. Use a field map, ModelRef, or RefUsage<ModelRef>.');
  }

  if (isExtendedRef(input)) {
    throw new Error('extendWith() does not support ExtendedRef. Use a field map, ModelRef, or RefUsage<ModelRef>.');
  }

  throw new Error('extendWith() only supports a field map, ModelRef, or RefUsage<ModelRef>.');
}

export function normalizeExtendWithInputWithSource(input: ExtendWithInput | undefined): NormalizedExtendWithWithSource | undefined {
  if (!input) return undefined;

  if (isModelRef(input)) {
    return {
      fields: input.fields,
      source: getSourceMetadataFromRef(input, 'extension'),
    };
  }

  if (isRefUsage(input)) {
    if (isModelRef(input.ref)) {
      // Prefer stored composition metadata if available
      if (input.usage.composition?.extensions && input.usage.composition.extensions.length > 0) {
        return {
          fields: input.ref.fields,
          source: input.usage.composition.extensions[input.usage.composition.extensions.length - 1],
        };
      }
      return {
        fields: input.ref.fields,
        source: getSourceMetadataFromRef(input.ref, 'extension'),
      };
    }

    throw new Error('extendWith() RefUsage must target a ModelRef.');
  }

  if (isSchemaCompositionFieldMap(input)) {
    return {
      fields: input,
      source: { origin: 'inline' },
    };
  }

  // Reject ComponentRef, PropertyRef, ArrayRef, ExtendedRef
  if (isComponentRef(input)) {
    throw new Error('extendWith() does not support ComponentRef. Use a field map, ModelRef, or RefUsage<ModelRef>.');
  }

  if (isPropertyRef(input)) {
    throw new Error('extendWith() does not support PropertyRef. Use a field map, ModelRef, or RefUsage<ModelRef>.');
  }

  if (isArrayRef(input)) {
    throw new Error('extendWith() does not support ArrayRef. Use a field map, ModelRef, or RefUsage<ModelRef>.');
  }

  if (isExtendedRef(input)) {
    throw new Error('extendWith() does not support ExtendedRef. Use a field map, ModelRef, or RefUsage<ModelRef>.');
  }

  throw new Error('extendWith() only supports a field map, ModelRef, or RefUsage<ModelRef>.');
}

function isModelRef(value: unknown): value is ModelRef {
  return !!value && typeof value === 'object' && 'kind' in value && value.kind === RefKind.model && 'fields' in value;
}

function isComponentRef(value: unknown): value is ComponentRef {
  return !!value && typeof value === 'object' && 'kind' in value && value.kind === RefKind.component;
}

function isPropertyRef(value: unknown): value is PropertyRef {
  return !!value && typeof value === 'object' && 'kind' in value && value.kind === RefKind.property;
}

function isArrayRef(value: unknown): value is { kind: 'array-ref' } {
  return !!value && typeof value === 'object' && 'kind' in value && value.kind === 'array-ref';
}

function isExtendedRef(value: unknown): value is { kind: 'extended-ref' } {
  return !!value && typeof value === 'object' && 'kind' in value && value.kind === 'extended-ref';
}

function isSchemaCompositionFieldMap(value: unknown): value is SchemaCompositionFieldMap {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return false;
  if (isModelRef(value)) return false;
  if (isRefUsage(value)) return false;
  if (isComponentRef(value)) return false;
  if (isPropertyRef(value)) return false;
  if (isArrayRef(value)) return false;
  if (isExtendedRef(value)) return false;

  return true;
}
