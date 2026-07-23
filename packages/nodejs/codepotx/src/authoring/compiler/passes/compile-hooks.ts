import type { CompiledHook } from '@/contract/index';
import type { RuntimeHookRegistry } from '../../hooks/hooks.types';
import { docsProperty, jsonObject, owner } from '../shared/compiler-values';

export function compileHooks(
  registries: readonly RuntimeHookRegistry[],
): readonly CompiledHook[] {
  return registries.flatMap((registry) =>
    registry.definitions.map((definition) => ({
      id: `hook:${owner(definition.owner)}:${definition.key}`,
      key: definition.key,
      name: definition.key,
      owner: owner(definition.owner),
      phase: definition.phase,
      ...(definition.transport ? { transport: 'runtime' } : {}),
      ...(definition.transport?.inbound
        ? { inbound: jsonObject(definition.transport.inbound) }
        : {}),
      ...(definition.transport?.outbound
        ? { outbound: jsonObject(definition.transport.outbound) }
        : {}),
      ...docsProperty(definition.info),
    })),
  );
}
