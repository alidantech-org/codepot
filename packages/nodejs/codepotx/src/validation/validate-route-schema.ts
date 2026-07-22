import type {
  RouteParameterRef,
  RouteRequestBodyRef,
  RouteResponseRef,
  RouteSchemaRef,
  RouteSchemaInput,
  RouteBodyInput,
  RouteResponseInput,
  RouteParameterMap,
} from '../routes/route.types.js';
import { RefKind } from '../refs/ref-kind.js';
import type { CompositeSchemaField, RecordSchemaField, OneOfSchemaField, AnyOfSchemaField } from '../schema/schema.types.js';
import { isEngineRef, isPropertyRef, isComponentRef } from './ref-guards.js';
import { isRefUsage } from './ref-usage-guards.js';
import { validateComponentFields } from './validate-component-fields.js';
import type { ValidationIssue } from './validation-result.types.js';
import { SchemaKind } from '../schema/schema-kind.js';

export type ValidatableRouteSchema =
  | RouteSchemaRef
  | RouteParameterRef
  | RouteRequestBodyRef
  | RouteResponseRef
  | RouteSchemaInput
  | RouteBodyInput
  | RouteResponseInput
  | RouteParameterMap
  | readonly unknown[];

export function validateRouteSchema(schema: ValidatableRouteSchema | undefined, path: string): ValidationIssue[] {
  if (!schema) return [];

  // Handle object-style inputs (body/response with schema property)
  if (typeof schema === 'object' && 'schema' in schema) {
    const objSchema = schema as { schema: RouteSchemaInput; description?: string };
    return validateRouteSchema(objSchema.schema, path);
  }

  // Handle parameter maps with route-specific validation
  if (path.includes('.params') || path.includes('.query')) {
    if (typeof schema === 'object' && !Array.isArray(schema) && !('schema' in schema)) {
      // For query, allow ComponentRef or RefUsage<ComponentRef>
      if (path.includes('.query')) {
        if (isComponentRef(schema)) {
          return [];
        }
        if (isRefUsage(schema) && isComponentRef(schema.ref)) {
          return [];
        }
      }
      // For params, only allow parameter maps (no component refs)
      return validateRouteParameterMap(schema as RouteParameterMap, path);
    }
  }

  if (Array.isArray(schema)) {
    return schema.flatMap((item, index) => validateRouteSchema(item as ValidatableRouteSchema, `${path}.${index}`));
  }

  if (isEngineRef(schema) || isRefUsage(schema)) return [];

  // Reject noContent in body/query/params
  if (path.includes('.body') || path.includes('.query') || path.includes('.params')) {
    if (isSchemaField(schema) && schema.kind === SchemaKind.noContent) {
      return [
        {
          path,
          message: 'schema.noContent() can only be used as a route response, not in body/query/params.',
        },
      ];
    }
  }

  // Validate as schema field
  if (isSchemaField(schema)) {
    // Recursively validate nested schemas
    if (schema.kind === SchemaKind.composite) {
      // Composite schemas are property definitions, not schema compositions
      // Skip validation here since property refs are validated when created through defineProperties().
      return [];
    }
    if (schema.kind === SchemaKind.record) {
      return validateRouteSchema((schema as RecordSchemaField).value, `${path}.value`);
    }
    if (schema.kind === SchemaKind.oneOf) {
      return (schema as OneOfSchemaField).values.flatMap((v, i) => validateRouteSchema(v, `${path}[${i}]`));
    }
    if (schema.kind === SchemaKind.anyOf) {
      return (schema as AnyOfSchemaField).values.flatMap((v, i) => validateRouteSchema(v, `${path}[${i}]`));
    }
    return [];
  }

  return validateComponentFields(schema as Parameters<typeof validateComponentFields>[0], path);
}

function validateRouteParameterMap(map: RouteParameterMap | undefined, path: string): ValidationIssue[] {
  if (!map) return [];

  const issues: ValidationIssue[] = [];

  for (const [name, value] of Object.entries(map)) {
    const currentPath = `${path}.${name}`;

    // Route parameters/query must be property refs or property ref usages
    if (isPropertyRef(value)) {
      continue;
    }

    if (isRefUsage(value)) {
      // Validate that the ref inside RefUsage is a property ref
      if (!isPropertyRef(value.ref)) {
        issues.push({
          path: currentPath,
          message: `Route query field "${name}" must be a property ref or property ref usage.`,
        });
      }
      continue;
    }

    // Reject anything else
    issues.push({
      path: currentPath,
      message: `Route query field "${name}" must be a property ref or property ref usage.`,
    });
  }

  return issues;
}

function isSchemaField(value: unknown): value is { kind: SchemaKind } {
  return !!value && typeof value === 'object' && 'kind' in value && typeof value.kind === 'string';
}
