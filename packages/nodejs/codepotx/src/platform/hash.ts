import { createHash } from 'node:crypto';

import type { ContentDigest, HashPort, JsonValue } from '@/contract/index';

function isJsonArray(value: JsonValue): value is readonly JsonValue[] {
  return Array.isArray(value);
}

function canonicalize(value: JsonValue): string {
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (isJsonArray(value)) return `[${value.map(canonicalize).join(',')}]`;

  return `{${Object.keys(value)
    .sort((left, right) => left.localeCompare(right))
    .map((key) => `${JSON.stringify(key)}:${canonicalize(value[key] ?? null)}`)
    .join(',')}}`;
}

function sha256(value: string | Buffer): ContentDigest {
  return createHash('sha256').update(value).digest('hex');
}

export class Sha256Hash implements HashPort {
  async text(value: string): Promise<ContentDigest> {
    return sha256(value);
  }

  async base64(value: string): Promise<ContentDigest> {
    return sha256(Buffer.from(value, 'base64'));
  }

  async values(values: readonly JsonValue[]): Promise<ContentDigest> {
    return sha256(canonicalize(values));
  }
}
