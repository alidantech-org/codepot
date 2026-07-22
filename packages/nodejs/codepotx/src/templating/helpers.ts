import Handlebars from 'handlebars';

import type { TemplateHelperDescriptor } from '@/contract/index';

interface HelperDefinition {
  readonly descriptor: TemplateHelperDescriptor;
  readonly implementation: (...args: unknown[]) => unknown;
}

/**
 * Built-in helpers are deterministic and side-effect free. Registering the full
 * set makes the documented helper catalog match the actual render runtime.
 */
const DEFINITIONS: readonly HelperDefinition[] = [
  helper('json', 'Serialize a value as formatted JSON.', ['value'], 'string', (value) => JSON.stringify(value, null, 2)),
  helper('lower', 'Convert a value to lower case.', ['value'], 'string', (value) => String(value).toLowerCase()),
  helper('upper', 'Convert a value to upper case.', ['value'], 'string', (value) => String(value).toUpperCase()),
  helper('camel', 'Convert a value to camelCase.', ['value'], 'string', (value) => words(value).map((word, index) => index === 0 ? word.toLowerCase() : capitalize(word)).join('')),
  helper('pascal', 'Convert a value to PascalCase.', ['value'], 'string', (value) => words(value).map(capitalize).join('')),
  helper('snake', 'Convert a value to snake_case.', ['value'], 'string', (value) => words(value).map((word) => word.toLowerCase()).join('_')),
  helper('kebab', 'Convert a value to kebab-case.', ['value'], 'string', (value) => words(value).map((word) => word.toLowerCase()).join('-')),
  helper('constant', 'Convert a value to CONSTANT_CASE.', ['value'], 'string', (value) => words(value).map((word) => word.toUpperCase()).join('_')),
  helper('title', 'Convert a value to title case.', ['value'], 'string', (value) => words(value).map(capitalize).join(' ')),
  helper('eq', 'Compare two values using strict equality.', ['left', 'right'], 'boolean', (left, right) => left === right),
  helper('not', 'Negate a value.', ['value'], 'boolean', (value) => !value),
  helper('and', 'Return true when every value is truthy.', ['values'], 'boolean', (...values) => values.slice(0, -1).every(Boolean)),
  helper('or', 'Return true when any value is truthy.', ['values'], 'boolean', (...values) => values.slice(0, -1).some(Boolean)),
  helper('contains', 'Test whether a string or array contains a value.', ['container', 'value'], 'boolean', (container, value) => Array.isArray(container) ? container.includes(value) : String(container).includes(String(value))),
  helper('length', 'Return string, array, or object length.', ['value'], 'number', (value) => Array.isArray(value) || typeof value === 'string' ? value.length : value && typeof value === 'object' ? Object.keys(value).length : 0),
  helper('join', 'Join array values with a separator.', ['values', 'separator'], 'string', (values, separator) => Array.isArray(values) ? values.join(separator === undefined ? ', ' : String(separator)) : String(values ?? '')),
  helper('concat', 'Concatenate values.', ['values'], 'string', (...values) => values.slice(0, -1).map(String).join('')),
  helper('default', 'Use a fallback for null, undefined, or empty string.', ['value', 'fallback'], 'unknown', (value, fallback) => value === undefined || value === null || value === '' ? fallback : value),
  helper('indent', 'Indent non-empty lines.', ['value', 'spaces'], 'string', (value, spaces) => {
    const prefix = ' '.repeat(Math.max(0, Number(spaces) || 0));
    return String(value).split('\n').map((line) => line ? `${prefix}${line}` : line).join('\n');
  }),
  helper('quote', 'Return a JSON-safe quoted string.', ['value'], 'string', (value) => JSON.stringify(String(value))),
];

export const BUILTIN_TEMPLATE_HELPERS: readonly TemplateHelperDescriptor[] = DEFINITIONS
  .map((item) => item.descriptor)
  .sort((left, right) => left.name.localeCompare(right.name));

export function createTemplateRenderer(requested: readonly string[]): typeof Handlebars {
  const renderer = Handlebars.create();
  const known = new Set(DEFINITIONS.map((item) => item.descriptor.name));
  for (const name of requested) {
    if (!known.has(name)) throw new Error(`Unknown Handlebars helper requested by template pack: ${name}`);
  }
  for (const item of DEFINITIONS) renderer.registerHelper(item.descriptor.name, item.implementation);
  return renderer;
}

function helper(
  name: string,
  description: string,
  args: readonly string[],
  returns: TemplateHelperDescriptor['returns'],
  implementation: (...args: unknown[]) => unknown,
): HelperDefinition {
  return {
    descriptor: {
      name,
      description,
      arguments: args.map((argument) => ({ name: argument, required: argument !== 'separator' })),
      returns,
      block: false,
    },
    implementation,
  };
}

function words(value: unknown): string[] {
  return String(value).replace(/([a-z0-9])([A-Z])/g, '$1 $2').split(/[^A-Za-z0-9]+/).filter(Boolean);
}

function capitalize(value: string): string {
  return value ? value[0]!.toUpperCase() + value.slice(1).toLowerCase() : value;
}
