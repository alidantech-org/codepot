import {
  PropertySlotSourceMode,
  EntityRelationKind,
  FieldPersistenceMode,
  type EntityFieldInput,
  type EntityFieldOptions,
  type FieldCapabilityConfig,
  type FieldLifecycleConfig,
  type FieldPersistenceConfig,
  type FieldVisibilityConfig,
} from '@/contract/types/authoring/4.properties-builder';

function isRelation(field: EntityFieldInput): boolean {
  return field.source.mode === PropertySlotSourceMode.relation;
}

function relationDefaultsToArray(field: EntityFieldInput): boolean {
  if (field.source.mode !== PropertySlotSourceMode.relation) return false;

  return field.source.relation === EntityRelationKind.hasMany || field.source.relation === EntityRelationKind.manyToMany;
}

function hasKeys(value: object): boolean {
  return Object.keys(value).length > 0;
}

function normalizeVisibility(options: EntityFieldOptions): FieldVisibilityConfig | undefined {
  if (options.visibility === undefined) {
    return {
      read: 'internal',
    };
  }

  return {
    ...(options.visibility.read !== undefined ? { read: options.visibility.read } : { read: 'internal' }),
    ...(options.visibility.write !== undefined ? { write: options.visibility.write } : {}),
    ...(options.visibility.sensitive !== undefined ? { sensitive: options.visibility.sensitive } : {}),
  };
}

function normalizeCapability(options: EntityFieldOptions): FieldCapabilityConfig | undefined {
  const capability = options.capability ?? {};

  return hasKeys(capability) ? capability : undefined;
}

function normalizeLifecycle(options: EntityFieldOptions): FieldLifecycleConfig | undefined {
  const lifecycle = options.lifecycle ?? {};

  return hasKeys(lifecycle) ? lifecycle : undefined;
}

function normalizePersistence(field: EntityFieldInput, options: EntityFieldOptions): FieldPersistenceConfig {
  const mode = options.persistence?.mode ?? (isRelation(field) ? FieldPersistenceMode.virtual : FieldPersistenceMode.stored);

  return {
    mode,
    ...(options.persistence?.generated !== undefined ? { generated: options.persistence.generated } : {}),
    ...(options.persistence?.immutable !== undefined ? { immutable: options.persistence.immutable } : {}),
  };
}

export function normalizeEntityFieldOptions(field: EntityFieldInput): EntityFieldOptions {
  const options = field.options ?? {};

  const visibility = normalizeVisibility(options);
  const capability = normalizeCapability(options);
  const lifecycle = normalizeLifecycle(options);
  const persistence = normalizePersistence(field, options);

  return {
    ...options,

    required: options.required ?? true,

    visibility,

    persistence,

    ...(options.nullable !== undefined ? { nullable: options.nullable } : {}),

    ...(options.array !== undefined ? { array: options.array } : relationDefaultsToArray(field) ? { array: true } : {}),

    ...(capability !== undefined ? { capability } : {}),

    ...(lifecycle !== undefined ? { lifecycle } : {}),
  };
}
