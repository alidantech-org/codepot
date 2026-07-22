// ─── codepurify/fields/transition.ts ─────────────────────────────────────────────────

import { FieldConfig } from '../types/base';
import { EnumFieldConfig } from '../types/enum';
import { TransitionConfig } from '../types/transition';

export function transition<TField extends FieldConfig>(config: TransitionConfig<TField>): TransitionConfig<TField> {
  return config;
}

// Helper function for enum field transitions with direct values access
export function enumTransition<T extends string>(
  values: Record<string, T>,
  config: {
    initial: T;
    terminal?: readonly T[];
    transitions: Record<T, readonly T[]>;
  },
): {
  field: () => EnumFieldConfig<T>;
  initial: T;
  terminal?: readonly T[];
  transitions: Record<T, readonly T[]>;
} {
  // Create a mock field function that returns the enum field config
  const mockField = () => ({ kind: 'enum' as const, values }) as EnumFieldConfig<T>;

  return {
    field: mockField,
    ...config,
  };
}
