// ─── codepurify/fields/foreign.ts ─────────────────────────────────────────────────

import type { BaseFieldConfig, BusinessConfig, SystemConfig } from './base';

// ─── Foreign field ────────────────────────────────────────────────────────────

export interface ForeignFieldConfig extends BaseFieldConfig {
  kind: 'foreign';
  business?: BusinessConfig;
  system?: SystemConfig;
}
