import type { Diagnostic } from '@/contract/index';
import { caughtDiagnostic } from '@/internal/results/operation-results';

export { failure, success } from '@/internal/results/operation-results';

export function diagnostic(code: string, caught: unknown): Diagnostic {
  return caughtDiagnostic('generation', code, caught);
}

export function error(code: string, message: string): Diagnostic {
  return { code, severity: 'error', layer: 'generation', message };
}
