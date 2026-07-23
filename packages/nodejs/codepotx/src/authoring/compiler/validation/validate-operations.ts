import type { CompiledOperation, Diagnostic } from '@/contract/index';

export function validateOperations(
  operations: readonly CompiledOperation[],
  diagnostics: Diagnostic[],
): void {
  const ids = new Set<string>();
  for (const operation of operations) {
    if (ids.has(operation.operationId)) {
      diagnostics.push({
        code: 'AUTHORING_DUPLICATE_OPERATION_ID',
        severity: 'error',
        layer: 'authoring',
        message: `Duplicate operation ID: ${operation.operationId}.`,
      });
    }
    ids.add(operation.operationId);
  }
  for (const operation of operations) {
    for (const target of operation.cacheInvalidates) {
      if (!ids.has(target)) {
        diagnostics.push({
          code: 'AUTHORING_UNKNOWN_CACHE_OPERATION',
          severity: 'error',
          layer: 'authoring',
          message: `Operation ${operation.operationId} invalidates unknown operation ${target}.`,
        });
      }
    }
  }
}
