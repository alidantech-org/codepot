import type { CompiledPropertyGroup } from '@/contract/index';
import type { PropertyRegistry } from '../../properties/property.types';
import { field } from '../schema/schema-normalizer';
import { dynamicObject, jsonObject } from '../shared/compiler-values';

export function compileProperties(
  registries: readonly PropertyRegistry[],
): readonly CompiledPropertyGroup[] {
  return registries.flatMap((registry) =>
    registry.definitions.map((definition) => ({
      id: `property-group:${registry.name}:${definition.name}`,
      key: definition.name,
      name: definition.name,
      properties: Object.entries(definition.fields).map(([key, value]) =>
        field(
          key,
          value,
          propertyRefId(registry, key)
            ?? `property:${definition.name}:${key}`,
        ),
      ),
      metadata: jsonObject({
        kind: definition.kind,
        emitSchema: definition.emitSchema ?? null,
        abstract: definition.abstract ?? null,
      }),
    })),
  );
}

function propertyRefId(
  registry: PropertyRegistry,
  key: string,
): string | undefined {
  const candidate = registry.ref[key];
  return dynamicObject(candidate) && typeof candidate.id === 'string'
    ? candidate.id
    : undefined;
}
