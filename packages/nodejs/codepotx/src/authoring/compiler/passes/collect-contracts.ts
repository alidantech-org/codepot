import type { CodepotConfig } from '../../config/config.types';
import type {
  SchemaComponentDefinition,
  SchemaComponentRegistry,
} from '../../components/component.types';
import type { VersionBuilder, VersionContract } from '../../version/version.types';

export interface SchemaEntry {
  readonly group: string;
  readonly definition: SchemaComponentDefinition;
  readonly id: string;
}

export function collectContracts(config: CodepotConfig): readonly VersionContract[] {
  return config.contracts.map(toContract);
}

export function collectSchemas(contracts: readonly VersionContract[]): readonly SchemaEntry[] {
  const output: SchemaEntry[] = [];
  const append = (registry: SchemaComponentRegistry): void => {
    for (const definition of registry.definitions) {
      output.push({
        group: registry.name,
        definition,
        id: registry.ref[definition.name]?.id
          ?? `component:schema:${definition.name}`,
      });
    }
  };

  for (const contract of contracts) {
    contract.schemaComponents.forEach(append);
    for (const resource of contract.resources) {
      resource.schemaComponents.forEach(append);
    }
  }
  return output;
}

function toContract(value: VersionBuilder | VersionContract): VersionContract {
  return 'contract' in value ? value.contract : value;
}
