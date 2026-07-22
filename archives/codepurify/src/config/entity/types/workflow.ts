// ─── codepurify/fields/workflow.ts ─────────────────────────────────────────────────

import type { FieldConfig } from './base';

// ─── Workflow Types ─────────────────────────────────────────────────────────────

export interface WorkflowFieldState {
  [fieldName: string]: string | boolean;
}

export interface WorkflowTransition {
  from: WorkflowFieldState;
  to: readonly WorkflowFieldState[];
}

export interface WorkflowConfig {
  key: string;
  fields: Record<string, () => FieldConfig>;
  initial: WorkflowFieldState;
  terminal: readonly WorkflowFieldState[];
  transitions: readonly WorkflowTransition[];
}
