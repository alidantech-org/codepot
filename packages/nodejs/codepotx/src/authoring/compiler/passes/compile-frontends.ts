import type { CompiledFrontend } from '@/contract/index';
import type { VersionContract } from '../../version/version.types';
import { docsProperty } from '../shared/compiler-values';

export function compileFrontends(
  contracts: readonly VersionContract[],
): readonly CompiledFrontend[] {
  return contracts.flatMap((contract) =>
    contract.frontends.map((frontend) => ({
      id: `frontend:${frontend.context.name}`,
      key: frontend.context.name,
      name: frontend.context.name,
      components: frontend.components,
      screens: frontend.screens,
      ...docsProperty(frontend.context.info),
      ...(frontend.context.metadata
        ? { metadata: frontend.context.metadata }
        : {}),
    })),
  );
}
