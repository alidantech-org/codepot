/**
 * Codepurify Object Utilities
 *
 * Provides object manipulation helpers for configuration merging and data processing.
 * Includes deep merge, type checking, and array utilities.
 */

/**
 * Checks if a value is a plain object (not array, null, or other types)
 *
 * @param value - Value to check
 * @returns True if value is a plain object
 */
export function isPlainObject(value: unknown): value is Record<string, unknown> {
  return (
    typeof value === 'object' && value !== null && !Array.isArray(value) && Object.prototype.toString.call(value) === '[object Object]'
  );
}

/**
 * Deeply merges two objects, with override values taking precedence
 *
 * @param base - Base object to merge into
 * @param override - Object with override values
 * @returns Merged object
 */
export function deepMerge<T>(base: T, override: Partial<T>): T {
  if (!isPlainObject(base) || !isPlainObject(override)) {
    return base;
  }

  const result = { ...base } as any;

  for (const key in override) {
    if (override[key] !== undefined) {
      const overrideValue = override[key];
      const baseValue = result[key];

      if (isPlainObject(overrideValue) && isPlainObject(baseValue)) {
        // Recursively merge plain objects
        result[key] = deepMerge(baseValue, overrideValue);
      } else {
        // For arrays, primitives, and other types, replace with override value
        result[key] = overrideValue;
      }
    }
  }

  return result;
}

/**
 * Removes undefined values from an object
 *
 * @param value - Object to process
 * @returns Object with undefined values removed
 */
export function omitUndefined<T extends Record<string, unknown>>(value: T): Partial<T> {
  const result: Partial<T> = {};

  for (const key in value) {
    if (value[key] !== undefined) {
      result[key] = value[key];
    }
  }

  return result;
}

/**
 * Compacts an array by removing null and undefined values
 *
 * @param value - Array to compact
 * @returns Array with null/undefined values removed
 */
export function compactArray<T>(value: Array<T | null | undefined>): T[] {
  return value.filter((item): item is T => item !== null && item !== undefined);
}
