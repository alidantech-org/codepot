import type { z } from '../schema/z-compat';
import { RefKind } from './ref-kind';
import type { RefMethodOptions } from './ref-methods.types';
import type {
  ExtendWithInput,
  FieldSourceMetadata,
  FieldSourceOrigin,
  RefUsage,
  RefUsageOptions,
  RefWithUsageMethods,
  SchemaProjection,
  SchemaProjectionDefinition,
  SchemaProjectionStep,
} from './ref-usage.types';
import type {
  ComponentRef,
  EngineRef,
  ModelRef,
  PropertyRef,
  RouteFieldSource,
  RouteSourceRef,
} from './ref.types';

export function withRefMethods<TRef extends EngineRef>(
  ref: TRef,
  options: RefMethodOptions = {},
): RefWithUsageMethods<TRef> {
  const target = ref as RefWithUsageMethods<TRef>;

  Object.defineProperties(target, {
    optional: method(() => createUsage(ref, { required: false }, options)),
    required: method(() => createUsage(ref, { required: true }, options)),
    nullable: method(() => createUsage(ref, { nullable: true }, options)),
    nonNullable: method(() => createUsage(ref, { nullable: false }, options)),
    array: method(() => createUsage(ref, { array: true }, options)),
    extendWith: method((fields: ExtendWithInput) => createUsage(ref, {
      extendWith: fields,
      composition: {
        base: sourceMetadataFromRef(ref, 'base'),
        extensions: [sourceMetadataFromExtension(fields)],
      },
    }, options)),
    zod: method(() => options.toZod?.(ref) ?? missingZodResolver(ref.id)),
    source: method((source: RouteFieldSource['route'] | RouteSourceRef) =>
      createUsage(ref, { source: normalizeRouteFieldSource(source) }, options)),
    allow: method((allow: Record<string, true>) => createAccessRoleSource(ref, allow)),
    partial: method(() => createProjectionDefinition(ref, 'partial')),
    pick: method((fields: Record<string, true | undefined>) =>
      createProjectionDefinition(ref, 'pick', fields)),
    omit: method((fields: Record<string, true | undefined>) =>
      createProjectionDefinition(ref, 'omit', fields)),
  });

  return target;
}

export function isRefUsage(value: unknown): value is RefUsage {
  return Boolean(value && typeof value === 'object' && 'ref' in value && 'usage' in value);
}

function method(value: (...args: never[]) => unknown): PropertyDescriptor {
  return { enumerable: false, configurable: true, value };
}

function createAccessRoleSource<TRef extends EngineRef>(
  ref: TRef,
  allow: Record<string, true>,
): { readonly source: PropertyRef; readonly allow: Readonly<Record<string, true>> } {
  if (ref.kind !== RefKind.property) {
    throw new Error(`Access allow maps can only be created from property refs: ${ref.id}`);
  }
  for (const [key, enabled] of Object.entries(allow)) {
    if (enabled !== true) {
      throw new Error(`Access allow value for "${key}" must be true. Use only { roleName: true }.`);
    }
  }
  return { source: ref, allow };
}

function createUsage<TRef extends EngineRef>(
  ref: TRef,
  usage: RefUsageOptions,
  options: RefMethodOptions,
): RefUsage<TRef> {
  const current = { ref, usage } as RefUsage<TRef>;
  Object.defineProperties(current, {
    optional: method(() => createUsage(ref, { ...usage, required: false }, options)),
    required: method(() => createUsage(ref, { ...usage, required: true }, options)),
    nullable: method(() => createUsage(ref, { ...usage, nullable: true }, options)),
    nonNullable: method(() => createUsage(ref, { ...usage, nullable: false }, options)),
    array: method(() => createUsage(ref, { ...usage, array: true }, options)),
    extendWith: method((fields: ExtendWithInput) => {
      const composition = usage.composition;
      return createUsage(ref, {
        ...usage,
        extendWith: fields,
        composition: {
          base: composition?.base ?? sourceMetadataFromRef(ref, 'base'),
          extensions: [...(composition?.extensions ?? []), sourceMetadataFromExtension(fields)],
        },
      }, options);
    }),
    zod: method(() => options.toZod?.(ref) ?? missingZodResolver(ref.id)),
    source: method((source: RouteFieldSource['route'] | RouteSourceRef) =>
      createUsage(ref, { ...usage, source: normalizeRouteFieldSource(source) }, options)),
  });
  return current;
}

function createProjectionDefinition<TRef extends EngineRef>(
  ref: TRef,
  mode: SchemaProjection['mode'],
  fields?: Record<string, true | undefined>,
): SchemaProjectionDefinition<TRef['name'], Record<string, unknown>, SchemaProjection['mode']> {
  const step = createProjectionStep(mode, fields);
  return withProjectionMethods({
    kind: 'schema-projection-definition',
    source: ref.name,
    sourceRefId: ref.id,
    mode: step.mode,
    ...(step.fields ? { fields: step.fields } : {}),
    steps: [step],
  });
}

function createChainedProjectionDefinition<
  TSourceName extends string,
  TFields extends Record<string, unknown>,
>(
  projection: SchemaProjectionDefinition<TSourceName, TFields, SchemaProjection['mode']>,
  mode: SchemaProjection['mode'],
  fields?: Record<string, true | undefined>,
): SchemaProjectionDefinition<TSourceName, TFields, SchemaProjection['mode']> {
  const step = createProjectionStep(mode, fields);
  return withProjectionMethods({
    kind: 'schema-projection-definition',
    source: projection.source,
    sourceRefId: projection.sourceRefId,
    mode: step.mode,
    ...(step.fields ? { fields: step.fields } : {}),
    steps: [
      ...(projection.steps ?? [{ mode: projection.mode, ...(projection.fields ? { fields: projection.fields } : {}) }]),
      step,
    ],
  });
}

function withProjectionMethods<
  TSourceName extends string,
  TFields extends Record<string, unknown>,
  TMode extends SchemaProjection['mode'],
>(
  projection: Omit<SchemaProjectionDefinition<TSourceName, TFields, TMode>, 'partial' | 'pick' | 'omit'>,
): SchemaProjectionDefinition<TSourceName, TFields, TMode> {
  const target = projection as SchemaProjectionDefinition<TSourceName, TFields, TMode>;
  Object.defineProperties(target, {
    partial: method(() => createChainedProjectionDefinition(target, 'partial')),
    pick: method((fields: Record<string, true | undefined>) => createChainedProjectionDefinition(target, 'pick', fields)),
    omit: method((fields: Record<string, true | undefined>) => createChainedProjectionDefinition(target, 'omit', fields)),
  });
  return target;
}

function createProjectionStep(
  mode: SchemaProjection['mode'],
  fields?: Record<string, true | undefined>,
): SchemaProjectionStep {
  return { mode, ...(fields ? { fields: projectionKeys(fields) } : {}) };
}

function projectionKeys(fields: Record<string, true | undefined>): readonly string[] {
  return Object.entries(fields).map(([key, enabled]) => {
    if (enabled !== true) {
      throw new Error(`Projection field "${key}" must be true. Use only { fieldName: true }.`);
    }
    return key;
  });
}

function sourceMetadataFromRef(ref: EngineRef, origin: FieldSourceOrigin): FieldSourceMetadata {
  switch (ref.kind) {
    case RefKind.component:
    case RefKind.model:
      return {
        origin,
        sourceRefId: ref.id,
        sourceSchemaName: ref.name,
        ...(ref.meta?.resource?.name ? { sourceResource: ref.meta.resource.name } : {}),
        ...(ref.meta?.shared === true ? { shared: true } : {}),
      };
    case RefKind.property:
      return {
        origin,
        propertyRefId: ref.id,
        fieldKey: ref.propertyKey,
        ...(ref.meta?.resource?.name ? { propertyResource: ref.meta.resource.name } : {}),
        ...(ref.meta?.shared === true ? { shared: true } : {}),
      };
    default:
      return { origin };
  }
}

function sourceMetadataFromExtension(input: ExtendWithInput): FieldSourceMetadata {
  if (isRefUsage(input)) {
    const last = input.usage.composition?.extensions?.at(-1);
    return last ?? sourceMetadataFromRef(input.ref, 'extension');
  }
  if ('kind' in input) {
    return sourceMetadataFromRef(input as ModelRef | ComponentRef, 'extension');
  }
  return { origin: 'inline' };
}

function normalizeRouteFieldSource(source: RouteFieldSource['route'] | RouteSourceRef): RouteFieldSource {
  if ('kind' in source && source.kind === 'route-source') {
    return { kind: 'route', route: source.route, source };
  }
  const sourceValues = Object.values(source.sources);
  if (sourceValues.length === 0) {
    throw new Error(`Route "${source.name}" has no sources. Add .source(...) before using it as a field source.`);
  }
  if (sourceValues.length > 1) {
    throw new Error(`Route "${source.name}" has multiple sources. Use route.sources.<name> explicitly.`);
  }
  const selected = sourceValues[0];
  if (!selected) throw new Error(`Route "${source.name}" has no resolvable source.`);
  return { kind: 'route', route: source, source: selected };
}

function missingZodResolver(refId: string): z.ZodTypeAny {
  throw new Error(`Zod resolver not provided for ref: ${refId}`);
}
