import { parse as parseYaml, stringify as stringifyYaml } from 'yaml';
import type { DataCodecPort, JsonValue } from '@/contract/index';

function toJsonSafe(value: unknown, path = '$'): JsonValue {
  if (value === null || typeof value === 'string' || typeof value === 'boolean') return value;
  if (typeof value === 'number') {
    if (!Number.isFinite(value)) throw new TypeError(`Non-finite number at ${path}.`);
    return value;
  }
  if (Array.isArray(value)) {
    return value.map((item, index) => toJsonSafe(item, `${path}[${String(index)}]`));
  }
  if (typeof value === 'object') {
    const prototype = Object.getPrototypeOf(value);
    if (prototype !== Object.prototype && prototype !== null) {
      throw new TypeError(`Non-JSON object at ${path}.`);
    }
    const output: Record<string, JsonValue> = {};
    for (const [key, item] of Object.entries(value)) {
      if (item !== undefined) output[key] = toJsonSafe(item, `${path}.${key}`);
    }
    return output;
  }
  throw new TypeError(`Non-JSON value at ${path}.`);
}

export class YamlJsonCodec implements DataCodecPort {
  parseJson<T = JsonValue>(text: string): T {
    return toJsonSafe(JSON.parse(text)) as T;
  }

  stringifyJson(value: unknown, options: { readonly pretty?: boolean } = {}): string {
    return `${JSON.stringify(toJsonSafe(value), null, options.pretty ? 2 : undefined)}\n`;
  }

  parseYaml<T = JsonValue>(text: string): T {
    return toJsonSafe(parseYaml(text)) as T;
  }

  stringifyYaml(value: unknown): string {
    return stringifyYaml(toJsonSafe(value));
  }
}
