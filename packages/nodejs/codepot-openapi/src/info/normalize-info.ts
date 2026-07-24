import type { InfoBuilder, InfoInput, InfoObject, InfoValue, NormalizedInfo } from './info.types.js';

const builtInCategories = [
  'explain',
  'implement',
  'warn',
  'important',
  'notice',
  'example',
  'security',
  'auth',
  'access',
  'privacy',
  'validation',
  'data',
  'persistence',
  'transaction',
  'migration',
  'performance',
  'caching',
  'testing',
  'observability',
  'errors',
  'ux',
  'accessibility',
  'i18n',
  'analytics',
  'compliance',
  'lifecycle',
  'dependency',
  'ai',
  'todo',
] as const;

export function normalizeInfo(input: InfoInput | undefined): NormalizedInfo | undefined {
  if (!input) return undefined;

  if (typeof input === 'function') {
    return cleanInfo(input(createInfoBuilder()).build());
  }

  const builder = createInfoBuilder();
  builder.use(input);
  return cleanInfo(builder.build());
}

export function createInfoBuilder(initial?: InfoInput): InfoBuilder {
  const state: Record<string, string[]> = {};

  const add = (category: string, value: InfoValue): void => {
    if (!category || typeof category !== 'string') {
      throw new Error('Info category must be a non-empty string.');
    }

    const values = normalizeInfoValue(category, value);
    const target = state[category] ?? [];

    for (const item of values) {
      if (!target.includes(item)) target.push(item);
    }

    state[category] = target;
  };

  const builder = {
    custom(category: string, value: InfoValue): InfoBuilder {
      add(category, value);
      return builder;
    },
    use(input: InfoObject | readonly InfoObject[]): InfoBuilder {
      for (const object of Array.isArray(input) ? input : [input]) {
        if (!object || typeof object !== 'object' || Array.isArray(object)) {
          throw new Error('Info use(...) expects an info object or array of info objects.');
        }

        for (const [category, value] of Object.entries(object) as Array<[string, InfoValue | undefined]>) {
          if (value !== undefined) add(category, value);
        }
      }

      return builder;
    },
    build(): NormalizedInfo {
      return Object.fromEntries(Object.entries(state).map(([key, values]) => [key, [...values]]));
    },
  } as InfoBuilder;

  for (const category of builtInCategories) {
    Object.assign(builder, {
      [category](value: InfoValue): InfoBuilder {
        add(category, value);
        return builder;
      },
    });
  }

  if (initial) {
    if (typeof initial === 'function') {
      initial(builder);
    } else {
      builder.use(initial);
    }
  }

  return builder;
}

function normalizeInfoValue(category: string, value: InfoValue): string[] {
  const values = Array.isArray(value) ? value : [value];

  return values.map((item) => {
    if (typeof item !== 'string') {
      throw new Error(`Info category "${category}" only accepts strings or string arrays.`);
    }

    return item.trim();
  }).filter(Boolean);
}

function cleanInfo(info: NormalizedInfo): NormalizedInfo | undefined {
  const cleaned = Object.fromEntries(Object.entries(info).filter(([, values]) => values.length > 0));
  return Object.keys(cleaned).length > 0 ? cleaned : undefined;
}
