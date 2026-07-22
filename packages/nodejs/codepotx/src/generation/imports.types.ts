import type { JsonObject, PlannedDependency, PortablePath } from '@/contract/index';

export interface GenerationImportRequest {
  readonly fromPath: PortablePath;
  readonly toPath: PortablePath;
  readonly dependency: PlannedDependency;
  readonly context: JsonObject;
}

export interface GenerationImportResult {
  readonly importPath: string;
  readonly statement?: string;
  readonly symbols?: readonly string[];
  readonly metadata?: JsonObject;
}

/** Language packs may replace the neutral relative-path import behavior. */
export interface GenerationImportAdapter {
  readonly id: string;
  resolve(request: GenerationImportRequest): GenerationImportResult;
}
