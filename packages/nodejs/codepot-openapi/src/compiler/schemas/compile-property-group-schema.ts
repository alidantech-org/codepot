import type { PropertyDefinition, PropertyRefGroup } from '../../properties/property.types.js';
import type { RefResolver } from '../refs/ref-resolver.types.js';
import { resolvePendingRefs } from '../refs/resolve-pending-refs.js';
import { applyCodegenMetadata } from '../../codegen/apply-codegen-extensions.js';
import type { CodegenMetadata } from '../../codegen/codegen-extension.types.js';

export function compilePropertyGroupSchema(
  definition: PropertyDefinition,
  refs: PropertyRefGroup,
  resolver: RefResolver,
): Record<string, unknown> {
  const required = Object.keys(refs);

  const schema: Record<string, unknown> = {
    type: 'object',
    properties: Object.fromEntries(
      Object.entries(refs as any).map(([key, ref]: [string, any]) => [key, resolvePendingRefs({ $ref: `#pending/${ref.targetRefId ?? ref.id}` }, resolver)]),
    ),
  };

  if (required.length > 0) {
    schema.required = required;
  }

  if (definition.kind === 'shared' || definition.abstract) {
    const codegenMeta: CodegenMetadata = {
      kind: 'model',
      shared: definition.kind === 'shared' ? true : undefined,
      abstract: definition.abstract ? true : undefined,
    };
    return applyCodegenMetadata(schema, codegenMeta);
  }

  return schema;
}
