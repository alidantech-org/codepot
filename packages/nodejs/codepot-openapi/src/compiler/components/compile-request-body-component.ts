import type { RequestBodyComponentDefinition } from '../../components/request-bodies/request-body-component.types.js';
import type { ComponentFieldMap } from '../../components/component.types.js';
import type { ComponentRef, ModelRef, RequestBodyRef } from '../../refs/ref.types.js';
import { ContentType } from '../../output/output.constants.js';
import { RefKind } from '../../refs/ref-kind.js';
import { isRefUsage } from '../../validation/ref-usage-guards.js';
import { applyCodegenMetadata } from '../../codegen/apply-codegen-extensions.js';
import { XCodegenDtoRole, XCodegenKind, type CodegenMetadata } from '../../codegen/codegen-extension.types.js';
import { compileComponentSchema } from '../schemas/compile-component-schema.js';
import { resolvePendingRefs } from '../refs/resolve-pending-refs.js';
import type { RefResolver } from '../refs/ref-resolver.types.js';

export function compileRequestBodyComponent(definition: RequestBodyComponentDefinition, resolver: RefResolver): Record<string, unknown> {
  const body: Record<string, unknown> = {
    required: definition.required ?? true,
    description: definition.description,
    content: {
      [ContentType.json]: {
        schema: resolvePendingRefs(toSchema(definition.schema), resolver),
      },
    },
  };

  if (definition.meta) {
    return applyCodegenMetadata(body, definition.meta);
  }

  return body;
}

function toSchema(schema: RequestBodyComponentDefinition['schema']): unknown {
  if (isRefUsage(schema)) return { $ref: `#pending/${schema.ref.id}` };
  if (isComponentRef(schema) || isModelRef(schema) || isRequestBodyRef(schema)) return { $ref: `#pending/${schema.id}` };

  return compileComponentSchema({
    name: 'InlineRequestBodySchema',
    value: schema as ComponentFieldMap,
  });
}

function isComponentRef(value: unknown): value is ComponentRef {
  return isRefKind(value, RefKind.component);
}

function isModelRef(value: unknown): value is ModelRef {
  return isRefKind(value, RefKind.model);
}

function isRequestBodyRef(value: unknown): value is RequestBodyRef {
  return isRefKind(value, RefKind.requestBody);
}

function isRefKind(value: unknown, kind: RefKind): boolean {
  return !!value && typeof value === 'object' && 'kind' in value && (value as { kind: RefKind }).kind === kind;
}
