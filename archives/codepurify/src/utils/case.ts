/**
 * Codepurify Case Utilities
 *
 * Provides naming case conversion helpers for code generation.
 * Handles various input formats and converts to different case styles.
 */

/**
 * Name variants for different case styles
 */
export interface NameVariants {
  /** Original input string */
  raw: string;
  /** camelCase */
  camel: string;
  /** PascalCase */
  pascal: string;
  /** kebab-case */
  kebab: string;
  /** snake_case */
  snake: string;
  /** SCREAMING_SNAKE_CASE */
  screamingSnake: string;
  /** Singular form */
  singular: string;
  /** Plural form */
  plural: string;
}

/**
 * Splits a string into words, handling various separators
 *
 * @param input - Input string to split
 * @returns Array of words
 */
export function toWords(input: string): string[] {
  if (!input) {
    return [];
  }

  // Handle different separators: camelCase, PascalCase, kebab-case, snake_case, spaces
  const words = input
    .replace(/([a-z])([A-Z])/g, '$1 $2') // camelCase -> camel case
    .replace(/([A-Z])([A-Z][a-z])/g, '$1 $2') // PascalCase -> Pascal Case
    .replace(/[-_]/g, ' ') // kebab-case, snake_case -> space
    .trim()
    .split(/\s+/) // split on whitespace
    .filter((word) => word.length > 0); // remove empty strings

  return words.map((word) => word.toLowerCase());
}

/**
 * Converts a string to camelCase
 *
 * @param input - Input string
 * @returns camelCase string
 */
export function toCamelCase(input: string): string {
  const words = toWords(input);
  if (words.length === 0) return '';

  const [first, ...rest] = words;
  return first + rest.map((word) => word.charAt(0).toUpperCase() + word.slice(1)).join('');
}

/**
 * Converts a string to PascalCase
 *
 * @param input - Input string
 * @returns PascalCase string
 */
export function toPascalCase(input: string): string {
  const words = toWords(input);
  return words.map((word) => word.charAt(0).toUpperCase() + word.slice(1)).join('');
}

/**
 * Converts a string to kebab-case
 *
 * @param input - Input string
 * @returns kebab-case string
 */
export function toKebabCase(input: string): string {
  const words = toWords(input);
  return words.join('-');
}

/**
 * Converts a string to snake_case
 *
 * @param input - Input string
 * @returns snake_case string
 */
export function toSnakeCase(input: string): string {
  const words = toWords(input);
  return words.join('_');
}

/**
 * Converts a string to SCREAMING_SNAKE_CASE
 *
 * @param input - Input string
 * @returns SCREAMING_SNAKE_CASE string
 */
export function toScreamingSnakeCase(input: string): string {
  return toSnakeCase(input).toUpperCase();
}

/**
 * Simple singularization (basic rules only)
 *
 * @param input - Input string
 * @returns Singular form
 */
export function singularize(input: string): string {
  const words = toWords(input);
  if (words.length === 0) return '';

  const lastWord = words[words.length - 1];
  let singularLastWord = lastWord;

  // Basic pluralization rules
  if (lastWord.endsWith('ies')) {
    singularLastWord = lastWord.slice(0, -3) + 'y';
  } else if (lastWord.endsWith('es') && !lastWord.endsWith('ss')) {
    singularLastWord = lastWord.slice(0, -2);
  } else if (lastWord.endsWith('s') && !lastWord.endsWith('ss')) {
    singularLastWord = lastWord.slice(0, -1);
  }

  words[words.length - 1] = singularLastWord;
  return words.join(' ');
}

/**
 * Simple pluralization (basic rules only)
 *
 * @param input - Input string
 * @returns Plural form
 */
export function pluralize(input: string): string {
  const words = toWords(input);
  if (words.length === 0) return '';

  const lastWord = words[words.length - 1];
  let pluralLastWord = lastWord;

  // Basic pluralization rules
  if (lastWord.endsWith('y') && !'aeiou'.includes(lastWord.charAt(lastWord.length - 2))) {
    pluralLastWord = lastWord.slice(0, -1) + 'ies';
  } else if (
    lastWord.endsWith('s') ||
    lastWord.endsWith('sh') ||
    lastWord.endsWith('ch') ||
    lastWord.endsWith('x') ||
    lastWord.endsWith('z')
  ) {
    pluralLastWord = lastWord + 'es';
  } else {
    pluralLastWord = lastWord + 's';
  }

  words[words.length - 1] = pluralLastWord;
  return words.join(' ');
}

/**
 * Creates all name variants from an input string
 *
 * @param input - Input string
 * @returns NameVariants object with all case styles
 */
export function createNameVariants(input: string): NameVariants {
  return {
    raw: input,
    camel: toCamelCase(input),
    pascal: toPascalCase(input),
    kebab: toKebabCase(input),
    snake: toSnakeCase(input),
    screamingSnake: toScreamingSnakeCase(input),
    singular: singularize(input),
    plural: pluralize(input),
  };
}
