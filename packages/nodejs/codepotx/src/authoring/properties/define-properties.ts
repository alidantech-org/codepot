import type { z } from '../schema/z-compat';
import { EngineIdPart, createEngineId } from '../core/engine-id';
import { RefKind } from '../refs/ref-kind';
import { withRefMethods } from '../refs/ref-methods';
import type { PropertyRef } from '../refs/ref.types';
import { SchemaKind } from '../schema/schema-kind';
import type { PrimitiveSchemaField } from '../schema/schema.types';
import type { DefinePropertiesOptions } from './define-properties.types';
import { PropertyKind } from './property-kind';
import type {
  PropertyDefinition,
  PropertyFieldRefMap,
  PropertyGroupOptions,
  PropertyGroupRegistry,
  ZodPropertyDefinitionFieldMap,
} from './property.types';

export function defineProperties<
  TName extends string,
  TFields extends ZodPropertyDefinitionFieldMap,
>(
  options: DefinePropertiesOptions,
  name: TName,
  fields: TFields,
  groupOptions: PropertyGroupOptions = {},
): PropertyGroupRegistry<PropertyFieldRefMap<TFields>> {
  const definitionFields = normalizeZodFields(fields);
  const schemas = new Map<string, z.ZodTypeAny>();
  const refs = Object.fromEntries(Object.entries(fields).map(([key, zod]) => {
    const id = createScopedId(options, EngineIdPart.property, name, key);
    schemas.set(id, zod);
    const ref = withRefMethods<PropertyRef>({
      id,
      name: key,
      kind: RefKind.property,
      propertyKey: key,
      meta: {
        kind: 'primitive',
        ...(!options.resource ? { shared: true } : {}),
        ...(options.resource ? { resource: { name: options.resource.alias, path: options.resource.folders } } : {}),
      },
    }, {
      toZod: (value) => {
        const selected = value as PropertyRef;
        const schema = schemas.get(selected.targetRefId ?? selected.id);
        if (!schema) throw new Error(`Zod schema not registered for ref: ${selected.id}`);
        return schema;
      },
    });
    return [key, ref];
  })) as PropertyFieldRefMap<TFields>;

  const definitions: readonly PropertyDefinition[] = [{
    kind: PropertyKind.shared,
    name,
    fields: definitionFields,
    ...(groupOptions.emitSchema === undefined ? {} : { emitSchema: groupOptions.emitSchema }),
    ...(groupOptions.abstract === undefined ? {} : { abstract: groupOptions.abstract }),
  }];

  return { name, definitions, ref: refs };
}

export function createScopedId(options: DefinePropertiesOptions, ...parts: readonly string[]): string {
  return options.resource
    ? createEngineId(EngineIdPart.resource, options.resource.name, ...parts)
    : createEngineId(...parts);
}

function normalizeZodFields<TFields extends ZodPropertyDefinitionFieldMap>(
  fields: TFields,
): Readonly<Record<keyof TFields & string, PrimitiveSchemaField>> {
  return Object.fromEntries(Object.entries(fields).map(([key, zod]) => [
    key,
    { kind: SchemaKind.primitive, zod },
  ])) as unknown as Readonly<Record<keyof TFields & string, PrimitiveSchemaField>>;
}
