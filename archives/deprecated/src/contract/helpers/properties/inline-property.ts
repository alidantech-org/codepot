import type { InlinePropertyPromotionHint, PropertySourceInput } from '@/contract/types/authoring/4.properties-builder';

function toSnake(value: string): string {
  return value
    .replace(/([a-z0-9])([A-Z])/g, '$1_$2')
    .replace(/[^a-zA-Z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '')
    .toLowerCase();
}

export function createInlinePropertyPromotionHint(input: {
  readonly ownerKind: 'entity' | 'composite';
  readonly ownerKey: string;
  readonly fieldKey: string;
}): InlinePropertyPromotionHint {
  return {
    ownerKind: input.ownerKind,
    ownerKey: input.ownerKey,
    fieldKey: input.fieldKey,
    suggestedKey: `${toSnake(input.ownerKind)}.${toSnake(input.ownerKey)}.${toSnake(input.fieldKey)}`,
  };
}

export function unwrapPropertySourceInput(value: PropertySourceInput | { readonly input: PropertySourceInput }): PropertySourceInput {
  if (value && typeof value === 'object' && 'input' in value) {
    return value.input;
  }

  return value;
}
