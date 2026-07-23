import type { CompiledInlineSchema } from '@/contract/index';
import { isProjection, jsonObject } from '../shared/compiler-values';
import { namedSchema } from './schema-normalizer';

/** Normalize named schemas while forcing projection metadata through JSON conversion. */
export function normalizeNamedSchema(value: unknown): CompiledInlineSchema {
  if (!isProjection(value)) return namedSchema(value);
  return {
    kind: 'object',
    fields: [],
    extends: [value.sourceRefId],
    additionalProperties: false,
    metadata: jsonObject({
      projection: {
        source: value.source,
        mode: value.mode,
        fields: value.fields ?? [],
        steps: value.steps ?? [],
      },
    }),
  };
}
