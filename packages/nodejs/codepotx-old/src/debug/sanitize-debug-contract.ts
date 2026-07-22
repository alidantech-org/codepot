import type { VersionContract } from '../version/version-contract.types.js';
import type { FieldSourceMetadata } from '../refs/ref-usage.types.js';
import { isRefUsage } from '../validation/ref-usage-guards.js';
import type { XCodegenResourceMeta } from '../codegen/codegen-extension.types.js';
import { resolveCodegenUi } from '../codegen/codegen-ui.js';
import { expressPathToOpenApi } from '../compiler/paths/express-path-to-openapi.js';

export function sanitizeDebugContract(value: unknown): unknown {
  const sanitized = sanitizeDebugValue(value);

  // If this is a VersionContract, add structured source metadata
  if (isVersionContract(value)) {
    return addSourceMetadataDebug(sanitized, value);
  }

  return sanitized;
}

function addSourceMetadataDebug(sanitized: unknown, contract: VersionContract): unknown {
  const debug: Record<string, unknown> = isRecord(sanitized) ? { ...sanitized } : {};

  // Extract source metadata from schema components
  const schemaComponentsDebug: Record<string, Record<string, unknown>> = {};

  // Process shared schema components
  for (const registry of contract.schemaComponents) {
    if (!isSchemaComponentRegistry(registry)) continue;

    const registryKey = 'shared';
    if (!schemaComponentsDebug[registryKey]) {
      schemaComponentsDebug[registryKey] = {};
    }

    for (const definition of registry.definitions) {
      const componentDebug = extractComponentSourceMetadata(definition.value);
      if (Object.keys(componentDebug).length > 0) {
        schemaComponentsDebug[registryKey][definition.name] = componentDebug;
      }
    }
  }

  // Process resource schema components
  for (const resource of contract.resources) {
    const resourceKey = 'resources';
    if (!schemaComponentsDebug[resourceKey]) {
      schemaComponentsDebug[resourceKey] = {};
    }

    for (const registry of resource.schemaComponents) {
      if (!isSchemaComponentRegistry(registry)) continue;

      for (const definition of registry.definitions) {
        const componentDebug = extractComponentSourceMetadata(definition.value);
        if (Object.keys(componentDebug).length > 0) {
          schemaComponentsDebug[resourceKey][definition.name] = componentDebug;
        }
      }
    }
  }

  if (Object.keys(schemaComponentsDebug).length > 0) {
    debug._sourceMetadata = schemaComponentsDebug;
  }

  const uiDebug = extractUiMetadataDebug(contract);

  if (uiDebug.length > 0) {
    debug._uiMetadata = uiDebug;
  }

  return debug;
}

function extractUiMetadataDebug(contract: VersionContract): unknown[] {
  const entries: unknown[] = [];

  for (const resource of contract.resources) {
    const resourcePath = expressPathToOpenApi(resource.context.route);

    for (const registry of resource.routeRegistries) {
      for (const route of Object.values(registry.routes)) {
        const fullPath = expressPathToOpenApi(`${resource.context.route}${route.path}`);
        const ui = resolveCodegenUi({
          operationUi: typeof route.ui === 'object' ? route.ui : undefined,
          resourceUi: resource.context.ui,
          method: route.method,
          fullPath,
          resourcePath,
        });

        entries.push({
          resource: resource.context.alias,
          operationId: route.operationId,
          path: fullPath,
          method: route.method,
          ui: {
            enabled: ui.enabled,
            role: ui.role,
            inferred: ui.inferred,
            inferenceReason: ui.inferenceReason,
          },
        });
      }
    }
  }

  return entries;
}

function extractComponentSourceMetadata(value: unknown): Record<string, unknown> {
  const debug: Record<string, unknown> = {};

  // Check if this is a RefUsage with extendWith
  if (isRefUsage(value)) {
    if (value.usage.composition) {
      debug.composition = sanitizeCompositionMetadata(value.usage.composition);
    }

    // Extract field-level source metadata if this has fields
    if (value.usage.extendWith) {
      debug.fields = extractExtendWithFieldsSource(value.usage.extendWith);
    }
  }

  return debug;
}

function sanitizeCompositionMetadata(composition: { base?: FieldSourceMetadata; extensions?: readonly FieldSourceMetadata[] }): unknown {
  const sanitized: Record<string, unknown> = {};

  if (composition.base) {
    sanitized.base = sanitizeFieldSourceMetadata(composition.base);
  }

  if (composition.extensions && composition.extensions.length > 0) {
    sanitized.extensions = composition.extensions.map(sanitizeFieldSourceMetadata);
  }

  return sanitized;
}

function sanitizeFieldSourceMetadata(metadata: FieldSourceMetadata): Record<string, unknown> {
  const sanitized: Record<string, unknown> = {
    origin: metadata.origin,
  };

  if (metadata.sourceSchemaName) sanitized.sourceSchemaName = metadata.sourceSchemaName;
  if (metadata.sourceResource) sanitized.sourceResource = metadata.sourceResource;
  if (metadata.shared !== undefined) sanitized.shared = metadata.shared;
  if (metadata.fieldKey) sanitized.fieldKey = metadata.fieldKey;
  if (metadata.propertyResource) sanitized.propertyResource = metadata.propertyResource;

  return sanitized;
}

function extractExtendWithFieldsSource(extendWith: unknown): Record<string, unknown> {
  const fieldsDebug: Record<string, unknown> = {};

  // If it's a field map (plain object)
  if (extendWith && typeof extendWith === 'object' && !Array.isArray(extendWith) && !('kind' in extendWith)) {
    for (const [name, field] of Object.entries(extendWith)) {
      if (isRefUsage(field) && field.ref.kind === 'property') {
        fieldsDebug[name] = sanitizeFieldSourceMetadata({
          origin: 'extension',
          propertyRefId: field.ref.id,
          fieldKey: field.ref.propertyKey,
          propertyResource: field.ref.meta?.resource ? (field.ref.meta.resource as XCodegenResourceMeta).name : undefined,
          shared: field.ref.meta?.shared === true,
        });
      } else if (typeof field === 'object' && 'kind' in field && field.kind === 'property') {
        fieldsDebug[name] = sanitizeFieldSourceMetadata({
          origin: 'extension',
          propertyRefId: (field as { id: string }).id,
          fieldKey: (field as { propertyKey: string }).propertyKey,
          propertyResource: (field as { meta?: { resource?: XCodegenResourceMeta } }).meta?.resource?.name,
          shared: (field as { meta?: { shared?: boolean } }).meta?.shared === true,
        });
      }
    }
  }

  return fieldsDebug;
}

function isVersionContract(value: unknown): value is VersionContract {
  return !!value && typeof value === 'object' && 'info' in value && 'resources' in value && 'schemaComponents' in value;
}

function isSchemaComponentRegistry(value: unknown): value is VersionContract['schemaComponents'][number] {
  return (
    !!value &&
    typeof value === 'object' &&
    !Array.isArray(value) &&
    'definitions' in value &&
    Array.isArray((value as { definitions?: unknown }).definitions)
  );
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return !!value && typeof value === 'object' && !Array.isArray(value);
}

function sanitizeDebugValue(value: unknown, seen = new WeakSet<object>()): unknown {
  if (typeof value === 'function') {
    return '[Function]';
  }

  if (value === null || typeof value !== 'object') {
    return value;
  }

  if (seen.has(value)) {
    return '[Circular]';
  }

  seen.add(value);

  if (Array.isArray(value)) {
    return value.map((item) => sanitizeDebugValue(item, seen));
  }

  const record = value as Record<string, unknown>;

  // Zod schemas should not be dumped raw.
  if ('_zod' in record || '_def' in record || 'toJSONSchema' in record) {
    return '[ZodSchema]';
  }

  const output: Record<string, unknown> = {};

  for (const [key, child] of Object.entries(record)) {
    if (typeof child === 'function') {
      continue;
    }

    // Avoid noisy internals
    if (key === 'zod') {
      output[key] = '[ZodSchema]';
      continue;
    }

    output[key] = sanitizeDebugValue(child, seen);
  }

  return output;
}
