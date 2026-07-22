import { createLogger } from '../logging/create-logger.js';
import type { Logger } from '../logging/logger.types.js';
import type { XCodegenDtoRole } from '../codegen/codegen-extension.types.js';

export interface CompilerContext {
  readonly logger?: Logger;
  /**
   * Tracks DTO component usage by role across route compilation.
   * Key: component ref id, Value: set of roles where this DTO is used.
   */
  readonly dtoRoleUsage?: Map<string, Set<XCodegenDtoRole>>;
  readonly accessContextSchemaIds?: Set<string>;
  readonly accessRolePropertyIds?: Set<string>;
}

export interface ResolvedCompilerContext {
  readonly logger: Logger;
  readonly dtoRoleUsage: Map<string, Set<XCodegenDtoRole>>;
  readonly accessContextSchemaIds: Set<string>;
  readonly accessRolePropertyIds: Set<string>;
}

export function resolveCompilerContext(context: CompilerContext = {}): ResolvedCompilerContext {
  return {
    logger: context.logger ?? createLogger({ level: 'silent' }),
    dtoRoleUsage: context.dtoRoleUsage ?? new Map(),
    accessContextSchemaIds: context.accessContextSchemaIds ?? new Set(),
    accessRolePropertyIds: context.accessRolePropertyIds ?? new Set(),
  };
}
