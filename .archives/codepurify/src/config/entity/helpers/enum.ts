import { FieldConfig, TransitionConfig, EnumFieldConfig } from '../types';

// Helper function to create typed enum value map
export function makeEnumValueMap<const T extends readonly string[]>(values: T): Record<T[number], T[number]> {
  return Object.fromEntries(values.map((value) => [value, value])) as Record<T[number], T[number]>;
}

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
