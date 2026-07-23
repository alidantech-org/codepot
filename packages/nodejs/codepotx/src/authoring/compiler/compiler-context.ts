import type {
  CompiledField,
  CompiledSchema,
  Diagnostic,
} from '@/contract/index';
import type { CodepotConfig } from '../config/config.types';
import type { VersionContract } from '../version/version.types';
import { collectContracts } from './passes/collect-contracts';

export interface AuthoringCompilerContext {
  readonly contracts: readonly VersionContract[];
  readonly diagnostics: Diagnostic[];
  readonly schemaFields: Map<string, readonly CompiledField[]>;
}

export function createCompilerContext(config: CodepotConfig): AuthoringCompilerContext {
  return {
    contracts: collectContracts(config),
    diagnostics: [],
    schemaFields: new Map<string, readonly CompiledField[]>(),
  };
}

export function indexSchemaFields(
  context: AuthoringCompilerContext,
  schemas: readonly CompiledSchema[],
): void {
  for (const schema of schemas) {
    context.schemaFields.set(
      schema.id,
      schema.schema.kind === 'object' ? schema.schema.fields : [],
    );
  }
}
