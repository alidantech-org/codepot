import type { VersionAuthoringState } from '@/contract/types/authoring/2.version-builder';
import type { CodepotDefinition } from '@/contract/types/ir/definition';

import { createCompilerContext } from './context/compiler-context';
import { compileContentTypes } from './passes/00-content-types';
import { compileProperties } from './passes/01-properties';
import { compileEntities } from './passes/02-entities';
import { compileRelations } from './passes/03-relations';
import { compileFieldSets } from './passes/04-field-sets';
import { compileModels } from './passes/04-models';
import { compileSchemas } from './passes/05-schemas';
import { compileSecurity } from './passes/06-security';
import { compileErrors } from './passes/07-errors';
import { compileResources } from './passes/08-resources';
import { compileMeta } from './passes/09-meta';
import { assertValidIrRefs } from './validators/ref-validator';

function throwIfDiagnosticsHaveErrors(
  diagnostics: readonly {
    readonly level: 'error' | 'warning';
    readonly path: string;
    readonly message: string;
  }[],
): void {
  const errors = diagnostics.filter((diagnostic) => diagnostic.level === 'error');

  if (errors.length === 0) return;

  throw new Error(errors.map((diagnostic) => `${diagnostic.path}: ${diagnostic.message}`).join('\n'));
}

export function compile(contract: VersionAuthoringState): CodepotDefinition {
  const ctx = createCompilerContext(contract);

  /**
   *  Pass 00: Compile content types.
   */
  compileContentTypes(ctx);

  /**
   * Pass 01: Compiles reusable property definitions (primitives, enums, composites).
   */
  compileProperties(ctx);

  /**
   * Pass 02: Compiles entity definitions with their fields.
   */
  compileEntities(ctx);

  /**
   * Pass 03: Compiles relation fields for entities.
   */
  compileRelations(ctx);

  /**
   * Pass 04: Compiles entity field-set overrides into IR schemas.field_sets.
   */
  compileFieldSets(ctx);

  /**
   * Pass 04: Compiles entity model variants into IR schemas.models.
   */
  compileModels(ctx);

  /**
   * Pass 05: Compiles DTOs and params schemas.
   */
  compileSchemas(ctx);

  /**
   * Pass 06: Compiles security definitions (credentials, principals, policies).
   */
  compileSecurity(ctx);

  /**
   * Pass 07: Compiles error definitions.
   */
  compileErrors(ctx);

  /**
   * Pass 08: Compiles API resources and routes.
   */
  compileResources(ctx);

  /**
   * Pass 09: Compiles root contract metadata (version, key, info, URLs).
   */
  compileMeta(ctx);

  throwIfDiagnosticsHaveErrors(ctx.diagnostics);
  assertValidIrRefs(ctx.ir);

  return ctx.ir;
}
