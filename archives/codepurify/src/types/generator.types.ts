/**
 * Codepurify Generator Types
 *
 * Shared types for generation inputs/outputs, file planning, and results.
 * Provides contracts for the generation system.
 */

export type GeneratedFileKind = 'context' | 'index' | 'entity' | 'repository' | 'dto' | 'service' | 'controller' | 'module';

export interface GeneratedFilePlan {
  kind: GeneratedFileKind;
  filePath: string;
  content: string;
  template: string;
  source: string;
  immutable: boolean;
  generator?: string;
}

export interface GenerationResult {
  written: number;
  skipped: number;
  failed: number;
}
