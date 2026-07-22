import { z } from 'zod';
import type { SchemaField } from '../schema/schema.types.js';
import type { RefUsage } from '../refs/ref-usage.types.js';
import type { PropertyRef, ModelRef, ComponentRef, EngineRef } from '../refs/ref.types.js';
import type { ZodSourceRegistry } from './zod-source-registry.js';
import { compileZodRef } from './compile-zod-ref.js';
import { isArrayRef, isExtendedRef } from '../refs/ref-wrapper-guards.js';

export function compileZodField(field: SchemaField, registry: ZodSourceRegistry): z.ZodTypeAny {
  // Handle wrapper refs
  if (isArrayRef(field) || isExtendedRef(field)) {
    return compileZodRef(field as any, registry);
  }

  // Handle refs (PropertyRef, ModelRef, ComponentRef)
  if (typeof field === 'object' && field !== null && 'id' in field && 'name' in field && 'kind' in field) {
    const ref = field as unknown as PropertyRef | ModelRef | ComponentRef;
    if (ref.kind === 'property' || ref.kind === 'model' || ref.kind === 'component') {
      return compileZodRef(ref, registry);
    }
  }

  switch (field.kind) {
    case 'primitive':
      return field.zod;

    case 'composite':
      return z.object(Object.fromEntries(Object.entries(field.fields).map(([key, value]) => [key, compileZodField(value, registry)])));

    case 'ref':
      return compileRefField(field.ref, registry);

    case 'record':
      return z.record(z.string(), compileZodField(field.value, registry));

    case 'literal':
      return z.literal(field.value);

    case 'oneOf':
      return z.union(field.values.map((value) => compileZodField(value, registry)) as [z.ZodTypeAny, z.ZodTypeAny, ...z.ZodTypeAny[]]);

    case 'anyOf':
      return z.union(field.values.map((value) => compileZodField(value, registry)) as [z.ZodTypeAny, z.ZodTypeAny, ...z.ZodTypeAny[]]);

    case 'file':
      return z.any();

    case 'noContent':
      return z.void();

    default:
      const _exhaustive: never = field;
      return _exhaustive;
  }
}

function compileRefField(
  ref: PropertyRef | ModelRef | ComponentRef | RefUsage<PropertyRef> | RefUsage<ModelRef> | RefUsage<ComponentRef>,
  registry: ZodSourceRegistry,
): z.ZodTypeAny {
  // Delegate RefUsage to compileZodRef which has full support for array/extendWith/nullable/optional
  if ('usage' in ref) {
    return compileZodRef(ref, registry);
  }

  const sourceField = registry.fields.get(ref.id);
  if (sourceField) {
    return compileZodField(sourceField, registry);
  }

  throw new Error(`Cannot resolve ref to Zod schema: ${ref.id}`);
}

function applyZodUsage(base: z.ZodTypeAny, usage: { required?: boolean; nullable?: boolean }): z.ZodTypeAny {
  let out = base;

  if (usage.nullable === true) out = out.nullable();
  if (usage.required === false) out = out.optional();

  return out;
}
