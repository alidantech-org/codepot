import type { VersionContract } from '../version/version-contract.types.js';
import type { ResolvedCompilerContext } from './compiler-context.js';
import { RefKind } from '../refs/ref-kind.js';
import type { PropertyRef } from '../refs/ref.types.js';
import type { AccessRegistry } from '../access/access.types.js';

export function collectAccessMetadataFromContract(contract: VersionContract, context: ResolvedCompilerContext): void {
  for (const registry of collectAccessRegistries(contract)) {
    for (const definition of registry.definitions) {
      const contextRef = definition.context;

      if (contextRef) {
        context.accessContextSchemaIds.add(contextRef.id);
      }

      for (const role of Object.values(definition.roles ?? {})) {
        const propertyRef = unwrapPropertyRef(role.source);
        if (propertyRef) {
          context.accessRolePropertyIds.add(propertyRef.id);
        }
      }
    }
  }
}

function collectAccessRegistries(contract: VersionContract): readonly AccessRegistry[] {
  return [...contract.accessComponents, ...contract.resources.flatMap((resource) => resource.accessComponents)];
}

function unwrapPropertyRef(value: unknown): PropertyRef | undefined {
  return isPropertyRef(value) ? value : undefined;
}

function isPropertyRef(value: unknown): value is PropertyRef {
  return !!value && typeof value === 'object' && (value as { kind?: unknown }).kind === RefKind.property;
}
