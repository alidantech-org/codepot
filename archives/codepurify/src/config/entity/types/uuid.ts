// ─── codepurify/fields/uuid.ts ─────────────────────────────────────────────────

import type { BaseFieldConfig } from './base';

// ─── UUID field ───────────────────────────────────────────────────────────────

export interface UuidFieldConfig extends BaseFieldConfig {
  kind: 'uuid';
  default?: string;
}
