// ─── codepurify/fields/transition.ts ─────────────────────────────────────────────────

import { FieldConfig } from './base';
import { BooleanFieldConfig } from './boolean';
import { EnumFieldConfig } from './enum';

// ─── Workflow Types ─────────────────────────────────────────────────────────────

// Helper type to extract enum values from EnumFieldConfig
export type EnumValues<T> = T extends EnumFieldConfig<infer V> ? V : never;

// Helper type to get transition value type based on field kind
type TransitionValueType<TField> = TField extends EnumFieldConfig<infer V> ? V : TField extends BooleanFieldConfig ? boolean : string;

// Helper type to get transitions record type based on field kind
type TransitionRecordType<TField> =
  TField extends EnumFieldConfig<infer V>
    ? Record<V, readonly V[]>
    : TField extends BooleanFieldConfig
      ? Record<string, readonly boolean[]>
      : Record<string, readonly (string | boolean)[]>;

export interface TransitionConfig<TField extends FieldConfig = FieldConfig> {
  field: () => TField;
  initial: TransitionValueType<TField>;
  terminal?: readonly TransitionValueType<TField>[];
  transitions: TransitionRecordType<TField>;
}
