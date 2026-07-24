import type { z } from 'zod';

import { EngineIdPart, createEngineId } from '../ids/engine-id.js';
import { toSchemaName } from '../naming/schema-name.js';
import { RefKind } from '../refs/ref-kind.js';
import { withRefMethods } from '../refs/ref-methods.js';
import type { GeneratedPropertySchema, PropertyRef } from '../refs/ref.types.js';
import type { RefWithUsageMethods } from '../refs/ref-usage.types.js';
import type { SchemaField, SchemaFieldMap } from '../schema/schema.types.js';
import { XCodegenKind } from '../codegen/codegen-extension.types.js';
import { isRefUsage } from '../validation/ref-usage-guards.js';

import type { DefinePropertiesOptions } from './define-properties.js';
import { PropertyKind } from './property-kind.js';
import type { PropertyFieldRefMap, PropertyRefGroup } from './property.types.js';

export function createPropertyRefs<TFields extends SchemaFieldMap>(
  options: DefinePropertiesOptions,
  name: string,
  fields: TFields,
  sourceKind: PropertyKind,
  toZod?: (ref: unknown) => z.ZodTypeAny,
): PropertyFieldRefMap<TFields> {
  return Object.fromEntries(
    Object.entries(fields).map(([key, field]) => [key, createPropertyRef(options, name, key, sourceKind, field, toZod)]),
  ) as PropertyFieldRefMap<TFields>;
}

export function createPropertyRef(
  options: DefinePropertiesOptions,
  name: string,
  key: string,
  sourceKind: PropertyKind,
  field: unknown,
  toZod?: (ref: unknown) => z.ZodTypeAny,
  generatedSchema?: GeneratedPropertySchema,
): RefWithUsageMethods<PropertyRef> {
  const refId = createScopedId(options, EngineIdPart.property, name, key);

  if (options.zodRegistry && typeof field === 'object' && field !== null && 'kind' in field) {
    options.zodRegistry.fields.set(refId, field as SchemaField);
  }

  return withRefMethods(
    {
      id: refId,
      name: key,
      kind: RefKind.property,
      propertyKey: key,
      targetRefId: getTargetRefId(field),
      generatedSchema,
      meta: {
        kind: XCodegenKind.primitive,
        ...(!options.resource && sourceKind === PropertyKind.shared ? { shared: true } : {}),
        resource: options.resource
          ? {
              name: options.resource.alias,
              path: options.resource.folders,
            }
          : undefined,
      },
    },
    { toZod },
  );
}

export function createScopedId(options: DefinePropertiesOptions, ...parts: string[]): string {
  if (!options.resource) return createEngineId(...parts);

  return createEngineId(EngineIdPart.resource, options.resource.name, ...parts);
}

export function getGeneratedPropertySchemaName(entityName: string, propertyName: string): string {
  return toSchemaName(`${entityName}${toSchemaName(propertyName)}`);
}

function getTargetRefId(field: unknown): string | undefined {
  if (isPropertyRef(field)) return field.targetRefId ?? field.id;

  if (isRefUsage(field) && isPropertyRef(field.ref)) {
    return field.ref.targetRefId ?? field.ref.id;
  }

  return undefined;
}

function isPropertyRef(value: unknown): value is PropertyRef {
  return !!value && typeof value === 'object' && 'kind' in value && value.kind === RefKind.property && 'propertyKey' in value;
}
