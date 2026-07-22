// ─── codepurify/types/indexes.ts ─────────────────────────────────────────────────

export interface IndexConfig {
  fields: readonly (() => any)[];
  unique?: boolean;
}
