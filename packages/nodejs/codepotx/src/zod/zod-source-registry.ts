import type { z } from 'zod';
import type { SchemaComponentDefinition } from '../components/schemas/schema-component.types.js';
import type { ModelRef } from '../refs/ref.types.js';
import type { SchemaField } from '../schema/schema.types.js';

export interface ZodSourceRegistry {
  readonly fields: Map<string, SchemaField>;
  readonly models: Map<string, ModelRef>;
  readonly schemas: Map<string, SchemaComponentDefinition>;
  readonly cache: Map<string, z.ZodTypeAny>;
  readonly compiling: Set<string>;
}

export function createZodSourceRegistry(): ZodSourceRegistry {
  return {
    fields: new Map(),
    models: new Map(),
    schemas: new Map(),
    cache: new Map(),
    compiling: new Set(),
  };
}
