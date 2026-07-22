import type { PropertyRef } from '../../refs/ref.types.js';
import type { SchemaField } from '../../schema/schema.types.js';
import { isZodEnum } from '../../schema/is-zod-enum.js';
import { applyCodegenMetadata } from '../../codegen/apply-codegen-extensions.js';
import { XCodegenKind, type CodegenMetadata } from '../../codegen/codegen-extension.types.js';
import { compilePropertySchema } from './compile-property-schema.js';
import type { CompilerContext } from '../compiler-context.js';

export function compileNamedPropertySchema(field: SchemaField, ref: PropertyRef, context?: CompilerContext): unknown {
  const schema = compilePropertySchema(field);

  if (!schema || typeof schema !== 'object' || Array.isArray(schema)) {
    return schema;
  }

  const isEnum = 'zod' in field && isZodEnum(field.zod);

  return applyCodegenMetadata(schema as Record<string, unknown>, buildFieldCodegenMetadata(field, ref, isEnum, context));
}

function buildFieldCodegenMetadata(field: SchemaField, ref: PropertyRef, isEnum: boolean, context?: CompilerContext): CodegenMetadata {
  const accessRole = context?.accessRolePropertyIds?.has(ref.id) ? { role: 'access-role' as const } : {};

  if (isEnum) {
    return {
      kind: XCodegenKind.enum,
      shared: ref.meta?.shared,
      resource: ref.meta?.resource,
      ...accessRole,
    };
  }

  return {
    kind: XCodegenKind.primitive,
    shared: ref.meta?.shared,
    resource: ref.meta?.resource,
    ...accessRole,
  };
}
