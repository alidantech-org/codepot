// src/compiler/context/diagnostics.ts

// ============================================================================
// DIAGNOSTIC TYPES
// ============================================================================

export const CompilerDiagnosticLevel = {
  error: 'error',
  warning: 'warning',
} as const;

export type CompilerDiagnosticLevel = (typeof CompilerDiagnosticLevel)[keyof typeof CompilerDiagnosticLevel];

export interface CompilerDiagnostic {
  readonly level: CompilerDiagnosticLevel;
  readonly path: string;
  readonly message: string;
}

export type CompilerDiagnostics = readonly CompilerDiagnostic[];

// ============================================================================
// CREATE
// ============================================================================

export function createCompilerDiagnostic(level: CompilerDiagnosticLevel, path: string, message: string): CompilerDiagnostic {
  return {
    level,
    path,
    message,
  };
}

// ============================================================================
// ADD
// ============================================================================

export function addCompilerError(diagnostics: CompilerDiagnostic[], path: string, message: string): void {
  diagnostics.push(createCompilerDiagnostic(CompilerDiagnosticLevel.error, path, message));
}

export function addCompilerWarning(diagnostics: CompilerDiagnostic[], path: string, message: string): void {
  diagnostics.push(createCompilerDiagnostic(CompilerDiagnosticLevel.warning, path, message));
}

// ============================================================================
// READ
// ============================================================================

export function getCompilerErrors(diagnostics: CompilerDiagnostics): readonly CompilerDiagnostic[] {
  return diagnostics.filter((diagnostic) => diagnostic.level === CompilerDiagnosticLevel.error);
}

export function hasCompilerErrors(diagnostics: CompilerDiagnostics): boolean {
  return getCompilerErrors(diagnostics).length > 0;
}

// ============================================================================
// FORMAT
// ============================================================================

export function formatCompilerDiagnostic(diagnostic: CompilerDiagnostic): string {
  return `${diagnostic.path}: ${diagnostic.message}`;
}

export function formatCompilerDiagnostics(diagnostics: CompilerDiagnostics): string {
  return diagnostics.map(formatCompilerDiagnostic).join('\n');
}

export function throwIfCompilerErrors(diagnostics: CompilerDiagnostics): void {
  const errors = getCompilerErrors(diagnostics);

  if (errors.length === 0) return;

  throw new Error(formatCompilerDiagnostics(errors));
}
