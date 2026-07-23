import type { CompiledAccessDefinition } from '@/contract/index';
import type { AccessRegistry } from '../../access/access.types';
import { docsProperty, jsonObject, owner } from '../shared/compiler-values';

export function compileAccess(
  registries: readonly AccessRegistry[],
): readonly CompiledAccessDefinition[] {
  return registries.flatMap((registry) =>
    registry.definitions.map((definition) => ({
      id: `access:${owner(definition.owner)}:${definition.key}`,
      key: definition.key,
      name: definition.key,
      owner: owner(definition.owner),
      roleSources: Object.entries(definition.roles ?? {}).map(
        ([key, role]) => jsonObject({
          key,
          source: role.source.id,
          allow: role.allow,
        }),
      ),
      allow: jsonObject({
        context: definition.context?.id ?? null,
        roles: Object.fromEntries(
          Object.entries(definition.roles ?? {}).map(
            ([key, role]) => [key, role.allow],
          ),
        ),
        tags: definition.tags ?? [],
      }),
      ...docsProperty(definition.info),
    })),
  );
}
