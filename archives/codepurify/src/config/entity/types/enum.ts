// ─── codepurify/fields/enum.ts ─────────────────────────────────────────────────

import type { BaseFieldConfig, TransitionState } from './base';

// ─── Enum field ───────────────────────────────────────────────────────────────

// Helper type to create typed enum value map
type EnumValueMap<T extends readonly string[]> = {
  readonly [K in T[number]]: K;
};

export interface EnumFieldConfig<V extends string> extends BaseFieldConfig {
  kind: 'enum';
  value_list: readonly V[];
  values: EnumValueMap<readonly V[]>;
  default?: V;
  state?: TransitionState<V>;
}
