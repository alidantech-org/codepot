// ─── codepurify/fields/entity.ts ─────────────────────────────────────────────────

import { FieldConfig, RelationConfigUnion, IndexConfig, IEntityConfig } from '../types';

// ─── Helper functions for entity configurations ───────────────────────────────────

export function defineFields<T extends Record<string, FieldConfig>>(fields: T): T {
  for (const [key, field] of Object.entries(fields)) {
    Object.defineProperty(field, 'key', {
      value: key,
      enumerable: true,
      configurable: true,
    });

    field.name!.original = key;
    field.name = toNameCases(key);
    field.type_name = field.name.pascal;
    field.constant_name = field.name.constant;
  }

  return fields;
}

// Enhanced canonical name cases parser
export interface NameVariantCases {
  original: string;
  parts: string[];
  parts_length: number;
  word: string;
  words: string;
  words_lower: string;
  words_upper: string;
  words_title: string;
  camel: string;
  pascal: string;
  snake: string;
  kebab: string;
  dot: string;
  slash: string;
  path: string;
  constant: string;
  train: string;
  lower: string;
  upper: string;
}

export interface NameCases extends NameVariantCases {
  singular: NameVariantCases;
  plural: NameVariantCases;
}

const irregularPlurals: Record<string, string> = {
  person: 'people',
  child: 'children',
  man: 'men',
  woman: 'women',
  mouse: 'mice',
  goose: 'geese',
  tooth: 'teeth',
  foot: 'feet',
};

const irregularSingulars = Object.fromEntries(Object.entries(irregularPlurals).map(([s, p]) => [p, s]));

function splitNameParts(input: string): string[] {
  return input
    .replace(/([a-z0-9])([A-Z])/g, '$1 $2')
    .replace(/([A-Z]+)([A-Z][a-z])/g, '$1 $2')
    .replace(/[_\-\s]+/g, ' ')
    .trim()
    .split(/\s+/)
    .filter(Boolean)
    .map((part) => part.toLowerCase());
}

function title(part: string): string {
  return part.charAt(0).toUpperCase() + part.slice(1);
}

function pluralizeWord(word: string): string {
  if (!word) return word;
  if (irregularPlurals[word]) return irregularPlurals[word];

  if (/(s|x|z|ch|sh)$/.test(word)) return `${word}es`;
  if (/[^aeiou]y$/.test(word)) return `${word.slice(0, -1)}ies`;
  if (/(?:f|fe)$/.test(word)) return word.replace(/(?:f|fe)$/, 'ves');

  return `${word}s`;
}

function singularizeWord(word: string): string {
  if (!word) return word;
  if (irregularSingulars[word]) return irregularSingulars[word];

  if (/(s|x|z|ch|sh)es$/.test(word)) return word.slice(0, -2);
  if (/[^aeiou]ies$/.test(word)) return `${word.slice(0, -3)}y`;
  if (/ves$/.test(word)) return `${word.slice(0, -3)}f`;
  if (/s$/.test(word) && !/ss$/.test(word)) return word.slice(0, -1);

  return word;
}

function buildNameVariantCases(original: string, parts: string[]): NameVariantCases {
  const words = parts.join(' ');
  const snake = parts.join('_');
  const kebab = parts.join('-');
  const pascal = parts.map(title).join('');
  const camel = parts.map((p, i) => (i === 0 ? p : title(p))).join('');

  return {
    original,
    parts,
    parts_length: parts.length,

    word: parts.at(-1) ?? '',
    words,
    words_lower: words,
    words_upper: words.toUpperCase(),
    words_title: parts.map(title).join(' '),

    camel,
    pascal,
    snake,
    kebab,
    dot: parts.join('.'),
    slash: parts.join('/'),
    path: parts.join('/'),
    constant: snake.toUpperCase(),
    train: parts.map(title).join('-'),
    lower: parts.join(''),
    upper: parts.join('').toUpperCase(),
  };
}

export function toNameCases(original: string): NameCases {
  const parts = splitNameParts(original);

  const singularParts = [...parts];
  singularParts[singularParts.length - 1] = singularizeWord(singularParts.at(-1) ?? '');

  const pluralParts = [...parts];
  pluralParts[pluralParts.length - 1] = pluralizeWord(pluralParts.at(-1) ?? '');

  return {
    ...buildNameVariantCases(original, parts),
    singular: buildNameVariantCases(original, singularParts),
    plural: buildNameVariantCases(original, pluralParts),
  };
}

export function defineRelations<const T extends Record<string, RelationConfigUnion>>(relations: T): T {
  return relations;
}

export function defineIndexes<const T extends readonly IndexConfig[]>(indexes: T): T {
  return indexes;
}

// ─── Entity definition ────────────────────────────────────────────────────────

export declare function defineEntityConfig<T extends IEntityConfig>(config: (self: T) => T): T;
