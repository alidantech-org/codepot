import { z } from 'zod';
import type { PropertyRef, ModelRef, ComponentRef, EngineRef } from '../refs/ref.types.js';
import type { ArrayRef, ExtendedRef } from '../refs/ref-wrapper.types.js';
import type { ComponentFieldMap } from '../components/component.types.js';
import type { SchemaComponentValue } from '../components/schemas/schema-component.types.js';
import type { RefUsage } from '../refs/ref-usage.types.js';
import type { ZodSourceRegistry } from './zod-source-registry.js';
import { compileZodField } from './compile-zod-field.js';
import { isArrayRef, isExtendedRef } from '../refs/ref-wrapper-guards.js';
import { isRefUsage } from '../validation/ref-usage-guards.js';
import { isEngineRef } from '../validation/ref-guards.js';
import { normalizeExtendWithInput } from '../compiler/schemas/normalize-extend-with.js';

export function compileZodRef(
  ref: PropertyRef | ModelRef | ComponentRef | ArrayRef<EngineRef> | ExtendedRef<EngineRef> | RefUsage<EngineRef>,
  registry: ZodSourceRegistry,
): z.ZodTypeAny {
  // Handle RefUsage first
  if (isRefUsage(ref)) {
    return compileRefUsage(ref, registry);
  }

  const cacheKey = getCacheKey(ref);

  // Check cache first
  const cached = registry.cache.get(cacheKey);
  if (cached) {
    return cached;
  }

  // Check for circular dependencies
  if (registry.compiling.has(cacheKey)) {
    throw new Error(`Circular dependency detected while compiling Zod schema for: ${cacheKey}`);
  }

  // Mark as compiling
  registry.compiling.add(cacheKey);

  try {
    const schema = compileZodRefInternal(ref, registry);

    // Cache the result
    registry.cache.set(cacheKey, schema);

    return schema;
  } finally {
    // Mark as done compiling
    registry.compiling.delete(cacheKey);
  }
}

function getCacheKey(ref: PropertyRef | ModelRef | ComponentRef | ArrayRef<EngineRef> | ExtendedRef<EngineRef>): string {
  if ('kind' in ref) {
    if (ref.kind === 'array-ref') {
      return `array:${getCacheKey(ref.ref as PropertyRef | ModelRef | ComponentRef)}`;
    }
    if (ref.kind === 'extended-ref') {
      if (!ref.fields) {
        throw new Error(`extended-ref is missing fields property: ${JSON.stringify(ref)}`);
      }
      const fieldsKey = Object.keys(ref.fields).sort().join(',');
      return `extended:${getCacheKey(ref.ref as PropertyRef | ModelRef | ComponentRef)}:${fieldsKey}`;
    }
  }
  if (!ref.id) {
    throw new Error(`ref is missing id property: ${JSON.stringify(ref)}`);
  }
  return ref.id;
}

function compileRefUsage(refUsage: RefUsage<EngineRef>, registry: ZodSourceRegistry): z.ZodTypeAny {
  const baseSchema = compileZodRef(refUsage.ref as PropertyRef | ModelRef | ComponentRef, registry);
  let schema = baseSchema;

  // Apply extendWith
  if (refUsage.usage.extendWith) {
    if (!('extend' in schema) || typeof schema.extend !== 'function') {
      throw new Error(`Cannot extend non-object Zod schema for ref: ${refUsage.ref.id}`);
    }
    const extensionFields = normalizeExtendWithInput(refUsage.usage.extendWith);
    if (extensionFields) {
      const extraShape = compileZodFieldMap(extensionFields, registry);
      schema = schema.extend(extraShape);
    }
  }

  // Apply array
  if (refUsage.usage.array) {
    schema = z.array(schema);
  }

  // Apply nullable
  if (refUsage.usage.nullable) {
    schema = schema.nullable();
  }

  // Apply optional
  if (refUsage.usage.required === false) {
    schema = schema.optional();
  }

  return schema;
}

function compileZodRefInternal(
  ref: PropertyRef | ModelRef | ComponentRef | ArrayRef<EngineRef> | ExtendedRef<EngineRef>,
  registry: ZodSourceRegistry,
): z.ZodTypeAny {
  if (isArrayRef(ref)) {
    return z.array(compileZodRef(ref.ref as PropertyRef | ModelRef | ComponentRef, registry));
  }

  if (isExtendedRef(ref)) {
    return compileExtendedRef(ref as ExtendedRef<PropertyRef | ModelRef | ComponentRef>, registry);
  }

  if (ref.kind === 'model') {
    return compileModelRef(ref, registry);
  }

  if (ref.kind === 'component') {
    return compileComponentRef(ref, registry);
  }

  if (ref.kind === 'property') {
    const sourceField = registry.fields.get(ref.id);
    if (sourceField) {
      return compileZodField(sourceField, registry);
    }
  }

  throw new Error(`Cannot resolve ref to Zod schema: ${ref.id}`);
}

function compileModelRef(modelRef: ModelRef, registry: ZodSourceRegistry): z.ZodTypeAny {
  const sourceFields = modelRef.sourceFields ?? {};
  const compiledFields = Object.fromEntries(Object.entries(sourceFields).map(([key, value]) => [key, compileZodField(value, registry)]));

  const baseSchema = z.object(compiledFields);

  if (modelRef.abstract) {
    return baseSchema.partial();
  }

  return baseSchema;
}

function compileComponentRef(componentRef: ComponentRef, registry: ZodSourceRegistry): z.ZodTypeAny {
  const definition = registry.schemas.get(componentRef.id);
  if (!definition) {
    throw new Error(`Cannot find schema component definition for ref: ${componentRef.id}`);
  }

  // Handle EngineRef (direct ref alias)
  if (isEngineRef(definition.value)) {
    // Only handle ComponentRef, ModelRef, or PropertyRef (schema refs)
    if (definition.value.kind === 'component' || definition.value.kind === 'model' || definition.value.kind === 'property') {
      return compileZodRef(definition.value, registry);
    }
    throw new Error(`Cannot compile schema component with ref kind: ${definition.value.kind}`);
  }

  // Handle RefUsage<EngineRef> (extendWith)
  if (isRefUsage(definition.value)) {
    return compileRefUsage(definition.value, registry);
  }

  // Handle ComponentFieldMap (normal object schema)
  const compiledFields = Object.fromEntries(
    Object.entries(definition.value as ComponentFieldMap).map(([key, value]) => {
      if (typeof value === 'object' && value !== null) {
        if ('id' in value && 'name' in value) {
          // It's a ref
          return [key, compileZodRef(value as any, registry)];
        }
      }
      return [key, compileZodField(value as any, registry)];
    }),
  );

  return z.object(compiledFields);
}

function compileExtendedRef(ref: ExtendedRef<PropertyRef | ModelRef | ComponentRef>, registry: ZodSourceRegistry): z.ZodTypeAny {
  const baseSchema = compileZodRef(ref.ref, registry);

  if (!('extend' in baseSchema) || typeof baseSchema.extend !== 'function') {
    throw new Error(`Cannot extend non-object Zod schema for ref: ${ref.ref.id}`);
  }

  const extraShape = compileZodFieldMap(ref.fields, registry);
  return baseSchema.extend(extraShape);
}

function compileZodFieldMap(fields: ComponentFieldMap, registry: ZodSourceRegistry): Record<string, z.ZodTypeAny> {
  return Object.fromEntries(Object.entries(fields).map(([key, field]) => [key, compileZodField(field as any, registry)]));
}

function compileExtendedFields(fields: Record<string, unknown>, registry: ZodSourceRegistry): Record<string, z.ZodTypeAny> {
  return Object.fromEntries(
    Object.entries(fields).map(([key, value]) => {
      if (typeof value === 'object' && value !== null) {
        if ('kind' in value && typeof value.kind === 'string') {
          // It's a SchemaField - compile it
          return [key, compileZodField(value as any, registry)];
        }
        if ('id' in value && 'name' in value) {
          // It's a ref - compile it
          return [key, compileZodRef(value as any, registry)];
        }
      }
      // Fallback: try to compile as field
      return [key, compileZodField(value as any, registry)];
    }),
  );
}

function isZodObject(schema: z.ZodTypeAny): schema is z.ZodObject<any> {
  return schema instanceof z.ZodObject;
}
