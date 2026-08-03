// cli/presentation/format-error.ts

// ============================================================================
// FORMAT
// ============================================================================

/**
 * Converts thrown values into readable CLI error messages.
 */
export function formatError(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }

  return String(error);
}
