// ─── codepurify/fields/string.ts ─────────────────────────────────────────────────

import type { BaseFieldConfig } from './base';

// ─── String field ─────────────────────────────────────────────────────────────

export interface StringFieldConfig extends BaseFieldConfig {
  kind: 'string';
  length?: number; // varchar when present, text when omitted
  default?: string;
}
