// ─── codepurify/fields/boolean.ts ─────────────────────────────────────────────────

import type { BaseFieldConfig, ToggleState } from './base';

// ─── Boolean field ────────────────────────────────────────────────────────────

export interface BooleanFieldConfig extends BaseFieldConfig {
  kind: 'boolean';
  default?: boolean;
  state?: ToggleState;
}
