import type { Diagnostic, OperationResult } from '@/contract/index';

export function success<T>(
  value: T,
  diagnostics: readonly Diagnostic[] = [],
): OperationResult<T> {
  return { success: true, value, diagnostics };
}

export function failure<T = never>(
  diagnostics: readonly Diagnostic[],
): OperationResult<T> {
  return { success: false, diagnostics };
}

export function caughtDiagnostic(
  layer: Diagnostic['layer'],
  code: string,
  caught: unknown,
): Diagnostic {
  return {
    code,
    severity: 'error',
    layer,
    message: caught instanceof Error ? caught.message : String(caught),
  };
}
