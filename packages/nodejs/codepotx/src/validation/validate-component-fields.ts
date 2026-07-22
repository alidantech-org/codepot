import type { ComponentFieldMap } from '../components/component.types.js';
import type { SchemaComponentValue } from '../components/schemas/schema-component.types.js';
import type { EngineRef } from '../refs/ref.types.js';
import { SchemaKind } from '../schema/schema-kind.js';
import { RefKind } from '../refs/ref-kind.js';
import { isComponentRef, isPropertyRef } from './ref-guards.js';
import { isRefUsage } from './ref-usage-guards.js';
import { isEngineRef } from './ref-guards.js';
import type { ValidationIssue } from './validation-result.types.js';
import { normalizeExtendWithInput } from '../compiler/schemas/normalize-extend-with.js';

export function validateComponentFields(fields: ComponentFieldMap, path = 'component.fields'): ValidationIssue[] {
  const issues: ValidationIssue[] = [];

  for (const [key, value] of Object.entries(fields)) {
    const currentPath = `${path}.${key}`;

    // Accept direct refs and ref usages
    if (isPropertyRef(value) || isComponentRef(value)) {
      continue;
    }

    // Don't recurse into ref objects
    if (isEngineRef(value)) {
      continue;
    }

    // Check ref usage has valid ref
    if (isRefUsage(value)) {
      if (!isEngineRef(value.ref)) {
        issues.push({
          path: currentPath,
          message: 'Component fields must be direct refs or ref usages.',
        });
      }
      continue;
    }

    // Reject schema helper fields (they have a 'kind' property)
    if (isSchemaField(value)) {
      issues.push({
        path: currentPath,
        message:
          'defineSchemas() fields must use existing refs/ref usages only. Use defineProperties() to create schema fields with schema.primitive(), schema.ref(), schema.record(), etc.',
      });
      continue;
    }

    if (isPlainObject(value)) {
      issues.push(...validateComponentFields(value, currentPath));
      continue;
    }

    issues.push({
      path: currentPath,
      message: 'Component fields must be direct refs or ref usages (e.g., ref, ref.array(), ref.nullable(), ref.optional()).',
    });
  }

  return issues;
}

export function validateSchemaComponentValue(value: SchemaComponentValue, path = 'component.value'): ValidationIssue[] {
  const issues: ValidationIssue[] = [];

  // Handle EngineRef (direct ref)
  if (isEngineRef(value)) {
    return issues;
  }

  // Handle RefUsage<EngineRef>
  if (isRefUsage(value)) {
    if (!isEngineRef(value.ref) && !('componentKey' in value.ref)) {
      issues.push({
        path,
        message: 'RefUsage must reference an EngineRef or ComponentRef.',
      });
    }
    // Validate extendWith if present
    if (value.usage.extendWith) {
      const extensionFields = normalizeExtendWithInput(value.usage.extendWith);
      if (extensionFields) {
        issues.push(...validateComponentFields(extensionFields, `${path}.extendWith`));
      }
    }
    return issues;
  }

  // Handle ComponentFieldMap (normal object schema)
  if (isPlainObject(value)) {
    return validateComponentFields(value, path);
  }

  issues.push({
    path,
    message: 'Schema component value must be a field map, EngineRef, or RefUsage<EngineRef>.',
  });

  return issues;
}

function isSchemaField(value: unknown): value is { kind: SchemaKind } {
  if (!value || typeof value !== 'object') return false;

  const obj = value as { kind?: string };
  if (!('kind' in obj) || typeof obj.kind !== 'string') return false;

  // Reject if kind is a RefKind (this means it's a ref, not a schema field)
  if (obj.kind === RefKind.property || obj.kind === RefKind.component || obj.kind === RefKind.model) {
    return false;
  }

  // Only reject if kind is a SchemaKind value
  const schemaKinds = [
    SchemaKind.primitive,
    SchemaKind.composite,
    SchemaKind.ref,
    SchemaKind.record,
    SchemaKind.literal,
    SchemaKind.oneOf,
    SchemaKind.anyOf,
    SchemaKind.file,
    SchemaKind.noContent,
  ];

  return schemaKinds.includes(obj.kind as SchemaKind);
}

function isPlainObject(value: unknown): value is ComponentFieldMap {
  return !!value && typeof value === 'object' && !Array.isArray(value);
}
