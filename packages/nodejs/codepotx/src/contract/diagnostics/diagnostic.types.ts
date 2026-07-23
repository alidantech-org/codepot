import type { JsonObject, PortablePath } from '../protocol/common.types';
import type { SourceLocation } from '../sources/source.types';

export type DiagnosticSeverity = 'error' | 'warning' | 'info' | 'debug';

export type DiagnosticLayer =
  | 'contract'
  | 'runtime'
  | 'platform'
  | 'authoring'
  | 'templating'
  | 'generation'
  | 'frontend';

export interface RelatedDiagnostic {
  readonly message: string;
  readonly location?: SourceLocation;
}

/** Structured diagnostic shared by all engines and frontends. */
export interface Diagnostic {
  readonly code: string;
  readonly severity: DiagnosticSeverity;
  readonly layer: DiagnosticLayer;
  readonly message: string;
  readonly location?: SourceLocation;
  readonly path?: PortablePath;
  readonly hints?: readonly string[];
  readonly related?: readonly RelatedDiagnostic[];
  readonly details?: JsonObject;
}

export interface ValidationResult {
  readonly valid: boolean;
  readonly diagnostics: readonly Diagnostic[];
}
