/**
 * Debounce Utility
 *
 * Simple debounce implementation for file watching.
 */

/**
 * Create a debounced version of a function.
 */
export function createDebounce<T extends (...args: any[]) => any>(fn: T, delayMs: number): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout | undefined;

  return (...args: Parameters<T>) => {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }

    timeoutId = setTimeout(() => {
      fn(...args);
    }, delayMs);
  };
}
