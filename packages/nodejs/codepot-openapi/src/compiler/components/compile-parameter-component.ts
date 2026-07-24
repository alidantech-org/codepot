import type { ParameterComponentDefinition } from '../../components/parameters/parameter-component.types.js';
import { RefKind } from '../../refs/ref-kind.js';
import { applyCodegenMetadata } from '../../codegen/apply-codegen-extensions.js';
import { resolvePendingRefs } from '../refs/resolve-pending-refs.js';
import type { RefResolver } from '../refs/ref-resolver.types.js';

export function compileParameterComponent(definition: ParameterComponentDefinition, resolver: RefResolver): Record<string, unknown> {
  const parameter: Record<string, unknown> = {
    name: definition.name,
    in: definition.in,
    required: definition.required ?? definition.in === 'path',
    description: definition.description,
    schema: resolvePendingRefs(toSchema(definition.schema), resolver),
  };

  if (definition.meta) {
    return applyCodegenMetadata(parameter, definition.meta);
  }

  return parameter;
}

function toSchema(schema: ParameterComponentDefinition['schema']): unknown {
  if ('ref' in schema) return { $ref: `#pending/${schema.ref.id}` };
  if ('id' in schema && schema.kind === RefKind.component) return { $ref: `#pending/${schema.id}` };
  if ('id' in schema) return { $ref: `#pending/${schema.id}` };

  return schema;
}
