import type { Diagnostic } from '@/contract/index';

export function diagnostic(code: string, caught: unknown): Diagnostic {
  return { code, severity: 'error', layer: 'generation', message: caught instanceof Error ? caught.message : String(caught) };
}
export function error(code: string, message: string): Diagnostic {
  return { code, severity: 'error', layer: 'generation', message };
}
export function success<T>(value: T, diagnostics: readonly Diagnostic[] = []): {
  readonly success: true;
  readonly value: T;
  readonly diagnostics: readonly Diagnostic[];
} {
  return { success: true, value, diagnostics };
}
export function failure(diagnostics: readonly Diagnostic[]): {
  readonly success: false;
  readonly diagnostics: readonly Diagnostic[];
} {
  return { success: false, diagnostics };
}
