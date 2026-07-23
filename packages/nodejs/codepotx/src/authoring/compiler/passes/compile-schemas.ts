import type { CompiledSchema } from '@/contract/index';
import { normalizeNamedSchema } from '../schema/normalize-named-schema';
import { docsProperty, jsonObject } from '../shared/compiler-values';
import type { SchemaEntry } from './collect-contracts';

export function compileSchemas(entries: readonly SchemaEntry[]): readonly CompiledSchema[] {
  return entries.map(({ group, definition, id }) => ({
    id,
    key: definition.name,
    name: definition.name,
    group,
    schema: normalizeNamedSchema(definition.value),
    ...docsProperty(definition.info),
    ...(definition.projection
      ? { metadata: jsonObject({ projection: definition.projection }) }
      : {}),
  }));
}
