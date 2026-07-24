import type { z } from 'zod';

import type { OptionalResourceContext } from '../resource/resource-context.types.js';
import { SchemaKind } from '../schema/schema-kind.js';
import type { PrimitiveSchemaField } from '../schema/schema.types.js';
import { compileZodRef } from '../zod/compile-zod-ref.js';

import { createPropertyRefs } from './property-ref.factory.js';
import { PropertyKind } from './property-kind.js';
import type {
  PropertyDefinition,
  PropertyFieldRefMap,
  PropertyGroupOptions,
  PropertyGroupRegistry,
  PropertyRegistry,
  ZodPropertyDefinitionFieldMap,
} from './property.types.js';

export interface DefinePropertiesOptions extends OptionalResourceContext {
  readonly name: string;
}

export function defineProperties<TName extends string, TFields extends ZodPropertyDefinitionFieldMap>(
  options: DefinePropertiesOptions,
  name: TName,
  fields: TFields,
  groupOptions: PropertyGroupOptions = {},
): PropertyGroupRegistry<PropertyFieldRefMap<TFields>> {
  const definitionFields = normalizeZodFields(fields);

  const definitions: PropertyDefinition[] = [
    {
      kind: PropertyKind.shared,
      name,
      fields: definitionFields,
      emitSchema: groupOptions.emitSchema,
      abstract: groupOptions.abstract,
    },
  ];

  const toZod = options.zodRegistry ? (ref: unknown): z.ZodTypeAny => compileZodRef(ref as never, options.zodRegistry!) : undefined;
  const groupRefs = createPropertyRefs(options, name, definitionFields, PropertyKind.shared, toZod) as unknown as PropertyFieldRefMap<TFields>;

  return {
    name,
    definitions,
    ref: groupRefs,
  };
}

function normalizeZodFields<TFields extends ZodPropertyDefinitionFieldMap>(
  fields: TFields,
): Record<keyof TFields & string, PrimitiveSchemaField> {
  return Object.fromEntries(
    Object.entries(fields).map(([key, zod]) => [
      key,
      {
        kind: SchemaKind.primitive,
        zod,
      },
    ]),
  ) as Record<keyof TFields & string, PrimitiveSchemaField>;
}
