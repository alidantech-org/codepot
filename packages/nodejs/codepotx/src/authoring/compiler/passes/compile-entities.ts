import type { CompiledEntity, CompiledField } from '@/contract/index';
import type { EntityDefinition, EntityRegistry } from '../../entities/entity.types';
import { queryMetadata } from '../schema/schema-normalizer';
import { docsProperty, jsonObject } from '../shared/compiler-values';

export function compileEntities(
  registries: readonly EntityRegistry[],
  schemaFields: ReadonlyMap<string, readonly CompiledField[]>,
): readonly CompiledEntity[] {
  return registries.flatMap((registry) =>
    registry.definitions.map((definition) =>
      compileEntity(definition, schemaFields),
    ),
  );
}

function compileEntity(
  definition: EntityDefinition,
  schemaFields: ReadonlyMap<string, readonly CompiledField[]>,
): CompiledEntity {
  const source = schemaFields.get(definition.schema.id) ?? [];
  const fields = source.map((item) => {
    const metadata = definition.fields[item.key];
    if (!metadata) return item;
    return {
      ...item,
      lifecycle: {
        selectable: metadata.select !== false,
        editable: metadata.edit !== false
          && metadata.readonly !== true
          && metadata.managed !== true,
        immutable: metadata.immutable === true,
        managed: metadata.managed === true || metadata.readonly === true,
      },
      query: queryMetadata(metadata.query),
      metadata: jsonObject({
        index: metadata.index ?? false,
        unique: metadata.unique ?? false,
        role: metadata.role ?? null,
        generated: metadata.generated ?? null,
      }),
    } satisfies CompiledField;
  });

  return {
    id: definition.ref.id,
    key: definition.key,
    name: definition.key,
    entityKind: definition.kind === 'abstract' ? 'base' : 'concrete',
    fields,
    ...(definition.extends ? { extends: definition.extends.id } : {}),
    constraints: Object.entries(definition.constraints ?? {}).map(
      ([key, constraint]) => ({
        id: `entity-constraint:${definition.ref.id}:${key}`,
        kind: constraint.kind,
        fields: constraint.fields ?? [],
        rules: constraint.rule ? [jsonObject(constraint.rule)] : [],
      }),
    ),
    relationIds: [],
    ...(definition.store ? { owner: definition.store } : {}),
    ...docsProperty(definition.info),
  };
}
