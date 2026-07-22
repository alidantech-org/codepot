import type { ComponentRef, EngineRef, ModelRef, PropertyRef } from './ref.types.js';
import type { FieldSourceMetadata, FieldSourceOrigin, ExtendWithInput } from './ref-usage.types.js';
import { RefKind } from './ref-kind.js';
import { isRefUsage } from '../validation/ref-usage-guards.js';
import type { XCodegenResourceMeta } from '../codegen/codegen-extension.types.js';

function resourceMetaToString(resource: XCodegenResourceMeta | undefined): string | undefined {
  if (!resource) return undefined;
  return resource.name;
}

export function getSourceMetadataFromRef(ref: EngineRef, origin: FieldSourceOrigin): FieldSourceMetadata {
  if (ref.kind === RefKind.component) {
    const componentRef = ref as ComponentRef;
    return {
      origin,
      sourceRefId: componentRef.id,
      sourceSchemaName: componentRef.name,
      sourceResource: resourceMetaToString(componentRef.meta?.resource),
      shared: componentRef.meta?.shared === true,
    };
  }

  if (ref.kind === RefKind.model) {
    const modelRef = ref as ModelRef;
    return {
      origin,
      sourceRefId: modelRef.id,
      sourceSchemaName: modelRef.name,
      sourceResource: resourceMetaToString(modelRef.meta?.resource),
      shared: modelRef.meta?.shared === true,
    };
  }

  if (ref.kind === RefKind.property) {
    const propertyRef = ref as PropertyRef;
    return {
      origin,
      propertyRefId: propertyRef.id,
      fieldKey: propertyRef.propertyKey,
      propertyResource: resourceMetaToString(propertyRef.meta?.resource),
      shared: propertyRef.meta?.shared === true,
    };
  }

  return { origin };
}

export function getSourceMetadataFromExtendWithInput(input: ExtendWithInput): FieldSourceMetadata {
  // If it's a RefUsage, check if it has composition metadata
  if (isRefUsage(input)) {
    if (input.usage.composition?.extensions && input.usage.composition.extensions.length > 0) {
      return input.usage.composition.extensions[input.usage.composition.extensions.length - 1];
    }
    // Fallback to ref metadata
    return getSourceMetadataFromRef(input.ref, 'extension');
  }

  // If it's a ModelRef or ComponentRef
  if (typeof input === 'object' && 'kind' in input) {
    return getSourceMetadataFromRef(input as EngineRef, 'extension');
  }

  // Inline field map
  return { origin: 'inline' };
}

export function isSharedRef(ref: EngineRef): boolean {
  if (ref.kind === RefKind.component) {
    const componentRef = ref as ComponentRef;
    return componentRef.meta?.shared === true;
  }
  if (ref.kind === RefKind.model) {
    const modelRef = ref as ModelRef;
    return modelRef.meta?.shared === true;
  }
  if (ref.kind === RefKind.property) {
    const propertyRef = ref as PropertyRef;
    return propertyRef.meta?.shared === true;
  }
  return false;
}
