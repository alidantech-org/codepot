import { EngineIdPart, createEngineId } from '../ids/engine-id.js';
import type { OptionalResourceContext } from '../resource/resource-context.types.js';
import type {
  BaseEntityDefinitionInput,
  ConcreteEntityDefinitionInput,
  EntityConstraintBuilder,
  EntityConstraintDefinition,
  EntityConstraintRule,
  EntityDefinition,
  EntityDefinitionInput,
  EntityFieldBuilder,
  EntityFieldMetadata,
  EntityFieldQueryBuilder,
  EntityFieldValueRef,
  EntityOwner,
  EntityRef,
  EntityRegistry,
  EntityRelation,
  EntityRelationBuilder,
  EntityRelationCardinality,
  EntityRelationDeleteBehavior,
  EntityRelationRef,
  EntityRelationRegistry,
  EntityRelationsInput,
  EntitySearchQueryOptions,
} from './entity.types.js';
import { normalizeInfo } from '../info/normalize-info.js';
import type { InfoInput } from '../info/info.types.js';

export interface DefineEntitiesOptions extends OptionalResourceContext {
  readonly name: string;
  readonly abstract?: boolean;
}

export type EntityDefinitionFactory<TInput extends Record<string, EntityDefinitionInput>> = (local: {
  readonly ref: { readonly [Key in keyof TInput & string]: EntityRef & { readonly name: Key } };
}) => TInput;

const entityDefinitionsByKey = new Map<string, EntityDefinition>();

export function defineBaseEntities<const TInput extends Record<string, BaseEntityDefinitionInput>>(
  input: TInput | EntityDefinitionFactory<TInput>,
): EntityRegistry<TInput> {
  return defineEntities({ name: 'base', abstract: true }, input as TInput | EntityDefinitionFactory<TInput>) as EntityRegistry<TInput>;
}

export function defineEntities<const TInput extends Record<string, EntityDefinitionInput>>(
  options: DefineEntitiesOptions,
  input: TInput | EntityDefinitionFactory<TInput>,
): EntityRegistry<TInput> {
  const owner = toOwner(options);
  const rawInput = resolveEntityInput(options, input, owner);
  const ref = createEntityRefs<TInput>(options, rawInput, owner);
  const definitions = Object.entries(rawInput).map(([key, value]) => {
    const entityRef = ref[key as keyof typeof ref] as EntityRef;
    const definition = normalizeEntityDefinition(key, value, entityRef, owner, !!options.abstract);
    entityDefinitionsByKey.set(entityRef.id, definition);
    return definition;
  });

  return {
    name: options.name,
    owner,
    abstract: !!options.abstract,
    definitions,
    ref,
  };
}

export function defineEntityRelations(owner: EntityOwner, input: EntityRelationsInput): EntityRelationRegistry {
  const builder = createRelationBuilder();
  const definitions: EntityRelation[] = [];

  for (const [source, relations] of Object.entries(input)) {
    for (const [name, createRelation] of Object.entries(relations)) {
      const relation = createRelation(builder);

      if (!relation.localField) {
        throw new Error(`Entity relation "${source}.${name}" must define local(...).`);
      }

      if (!relation.foreignField) {
        throw new Error(`Entity relation "${source}.${name}" must define foreign(...).`);
      }

      definitions.push({
        source,
        name,
        cardinality: relation.cardinality,
        target: relation.target,
        local: relation.localField,
        foreign: relation.foreignField,
        onDelete: relation.deleteBehavior,
      });
    }
  }

  return { owner, definitions };
}

export function getEntityDefinition(ref: EntityRef): EntityDefinition | undefined {
  return entityDefinitionsByKey.get(ref.id);
}

function resolveEntityInput<const TInput extends Record<string, EntityDefinitionInput>>(
  options: DefineEntitiesOptions,
  input: TInput | EntityDefinitionFactory<TInput>,
  owner: EntityOwner,
): TInput {
  if (typeof input !== 'function') return input;

  const localRef = new Proxy(
    {},
    {
      get(_target, key) {
        if (typeof key !== 'string') return undefined;
        return createEntityRef(options, key, owner, !!options.abstract);
      },
    },
  ) as { readonly [Key in keyof TInput & string]: EntityRef & { readonly name: Key } };

  return input({ ref: localRef });
}

function createEntityRefs<const TInput extends Record<string, EntityDefinitionInput>>(
  options: DefineEntitiesOptions,
  input: TInput,
  owner: EntityOwner,
): EntityRegistry<TInput>['ref'] {
  return Object.fromEntries(
    Object.keys(input).map((key) => [key, createEntityRef(options, key, owner, !!options.abstract)] as const),
  ) as EntityRegistry<TInput>['ref'];
}

function createEntityRef(options: DefineEntitiesOptions, key: string, owner: EntityOwner, abstract: boolean): EntityRef {
  return {
    id: createEntityId(options, key),
    name: key,
    kind: 'entity',
    entityKey: key,
    owner,
    abstract,
  };
}

function createEntityId(options: DefineEntitiesOptions, key: string): string {
  if (options.resource) {
    return createEngineId(EngineIdPart.resource, options.resource.name, 'entity', key);
  }

  return createEngineId('entity', options.abstract ? 'base' : options.name, key);
}

function normalizeEntityDefinition(
  key: string,
  input: EntityDefinitionInput,
  ref: EntityRef,
  owner: EntityOwner,
  abstractRegistry: boolean,
): EntityDefinition {
  if (abstractRegistry || input.kind === 'abstract') {
    const base = input as BaseEntityDefinitionInput;

    if ('store' in base) {
      throw new Error(`Abstract entity "${key}" must not define store.`);
    }

    return {
      key,
      kind: 'abstract',
      schema: base.schema,
      extends: base.extends,
      fields: buildFieldMetadata(base.fields),
      info: normalizeInfo(base.info),
      owner,
      ref,
    };
  }

  const concrete = input as ConcreteEntityDefinitionInput;

  if (!concrete.store) {
    throw new Error(`Concrete entity "${key}" must define store.`);
  }

  return {
    key,
    kind: 'entity',
    schema: concrete.schema,
    extends: concrete.extends,
    store: concrete.store,
    backend: concrete.backend,
    fields: buildFieldMetadata(concrete.fields),
    constraints: concrete.constraints?.(createConstraintBuilder()),
    info: normalizeInfo(concrete.info),
    owner,
    ref,
  };
}

function buildFieldMetadata(fields: Record<string, (field: EntityFieldBuilder) => EntityFieldBuilder> | undefined): Record<string, EntityFieldMetadata> {
  if (!fields) return {};

  if (typeof fields === 'function') {
    throw new Error('Entity fields must use object-key syntax: fields: { fieldName: ($) => ... }.');
  }

  return Object.fromEntries(
    Object.entries(fields).map(([key, createField]) => {
      const builder = createEntityFieldBuilder();
      const result = createField(builder);
      return [key, getEntityFieldMetadata(result)];
    }),
  );
}

function createEntityFieldBuilder(initial: EntityFieldMetadata = {}): EntityFieldBuilder {
  const metadata = { ...initial };

  return {
    index: () => createEntityFieldBuilder({ ...metadata, index: true }),
    unique: () => createEntityFieldBuilder({ ...metadata, unique: true }),
    readonly: () => createEntityFieldBuilder({ ...metadata, readonly: true, edit: false }),
    managed: () => createEntityFieldBuilder({ ...metadata, managed: true, readonly: true, edit: false }),
    immutable: () => createEntityFieldBuilder({ ...metadata, immutable: true }),
    select: (enabled) => createEntityFieldBuilder(enabled === false ? { ...metadata, select: false } : metadata),
    edit: (enabled) => createEntityFieldBuilder(enabled === false ? { ...metadata, edit: false } : metadata),
    role: (role) => createEntityFieldBuilder({ ...metadata, role }),
    generated: (generated) => createEntityFieldBuilder({ ...metadata, generated }),
    query: (callback) => {
      const query = callback(createEntityFieldQueryBuilder());
      return createEntityFieldBuilder({ ...metadata, query: getEntityFieldQueryMetadata(query) });
    },
    info: (info: InfoInput) => createEntityFieldBuilder({ ...metadata, info: normalizeInfo(info) }),
    __metadata: metadata,
  } as EntityFieldBuilder & { readonly __metadata: EntityFieldMetadata };
}

function getEntityFieldMetadata(builder: EntityFieldBuilder): EntityFieldMetadata {
  return (builder as EntityFieldBuilder & { readonly __metadata?: EntityFieldMetadata }).__metadata ?? {};
}

function createEntityFieldQueryBuilder(initial: Record<string, unknown> = {}): EntityFieldQueryBuilder {
  const metadata = { ...initial };

  return {
    exact: () => createEntityFieldQueryBuilder({ ...metadata, exact: true }),
    oneOf: () => createEntityFieldQueryBuilder({ ...metadata, oneOf: true }),
    range: () => createEntityFieldQueryBuilder({ ...metadata, range: true }),
    date: () => createEntityFieldQueryBuilder({ ...metadata, date: true }),
    sort: () => createEntityFieldQueryBuilder({ ...metadata, sort: true }),
    search: (options) => {
      validateSearchOptions(options);
      return createEntityFieldQueryBuilder({ ...metadata, search: cleanSearchOptions(options) });
    },
    __metadata: metadata,
  } as EntityFieldQueryBuilder & { readonly __metadata: Record<string, unknown> };
}

function getEntityFieldQueryMetadata(builder: EntityFieldQueryBuilder): EntityFieldMetadata['query'] {
  return (builder as EntityFieldQueryBuilder & { readonly __metadata?: EntityFieldMetadata['query'] }).__metadata ?? {};
}

function validateSearchOptions(options: EntitySearchQueryOptions): void {
  if (!options || typeof options !== 'object' || Array.isArray(options)) {
    throw new Error('Entity query search(...) expects an object with boolean prefix/contains/fuzzy flags.');
  }

  if ('modes' in options) {
    throw new Error('Entity query search(...) uses boolean flags, not search.modes.');
  }

  if (!options.prefix && !options.contains && !options.fuzzy) {
    throw new Error('Entity query search(...) requires at least one true option: prefix, contains, or fuzzy.');
  }
}

function cleanSearchOptions(options: EntitySearchQueryOptions): EntitySearchQueryOptions {
  return {
    ...(options.prefix ? { prefix: true } : {}),
    ...(options.contains ? { contains: true } : {}),
    ...(options.fuzzy ? { fuzzy: true } : {}),
  };
}

function createConstraintBuilder(): EntityConstraintBuilder {
  const compare = (op: string, field: string, value: unknown): EntityConstraintRule => ({ op, field, value });

  return {
    index: (fields) => ({ kind: 'index', fields }),
    unique: (fields) => ({ kind: 'unique', fields }),
    check: (rule) => ({ kind: 'check', rule }),
    gt: (field, value) => compare('gt', field, value),
    gte: (field, value) => compare('gte', field, value),
    lt: (field, value) => compare('lt', field, value),
    lte: (field, value) => compare('lte', field, value),
    eq: (field, value) => compare('eq', field, value),
    neq: (field, value) => compare('neq', field, value),
    notNull: (field) => ({ op: 'notNull', field }),
    oneOf: (field, values) => ({ op: 'oneOf', field, values }),
    range: (field, min, max) => ({ op: 'range', field, min, max }),
    when: (condition, thenCondition) => ({ op: 'when', condition, then: thenCondition }),
    and: (...conditions) => ({ op: 'and', conditions }),
    or: (...conditions) => ({ op: 'or', conditions }),
    field: (fieldName): EntityFieldValueRef => ({ $field: fieldName }),
  };
}

function createRelationBuilder(): EntityRelationBuilder {
  const create = (cardinality: EntityRelationCardinality, target: EntityRef): EntityRelationRef => {
    const state: {
      localField?: string;
      foreignField?: string;
      deleteBehavior?: EntityRelationDeleteBehavior;
    } = {};

    const relation: EntityRelationRef = {
      cardinality,
      target,
      get localField() {
        return state.localField;
      },
      get foreignField() {
        return state.foreignField;
      },
      get deleteBehavior() {
        return state.deleteBehavior;
      },
      local(field: string) {
        state.localField = field;
        return relation;
      },
      foreign(field: string) {
        state.foreignField = field;
        return relation;
      },
      onDelete(behavior: EntityRelationDeleteBehavior) {
        state.deleteBehavior = normalizeDeleteBehavior(behavior);
        return relation;
      },
    } satisfies EntityRelationRef;

    return relation;
  };

  return {
    belongsTo: (target) => create('belongsTo', target),
    hasOne: (target) => create('hasOne', target),
    hasMany: (target) => create('hasMany', target),
    manyToMany: (target) => create('manyToMany', target),
  };
}

function normalizeDeleteBehavior(behavior: EntityRelationDeleteBehavior): EntityRelationDeleteBehavior {
  if (!behavior || typeof behavior !== 'object' || Array.isArray(behavior)) {
    throw new Error('Entity relation onDelete(...) expects a boolean options object.');
  }

  const enabled = Object.entries(behavior).filter(([, value]) => value === true);

  if (enabled.length !== 1) {
    throw new Error('Entity relation onDelete(...) requires exactly one true option.');
  }

  const [key] = enabled[0];

  if (!['cascade', 'restrict', 'setNull', 'noAction'].includes(key)) {
    throw new Error(`Entity relation onDelete(...) option "${key}" is not supported.`);
  }

  return { [key]: true };
}

function toOwner(options: DefineEntitiesOptions): EntityOwner {
  if (options.resource) {
    return {
      resource: {
        name: options.resource.alias,
        path: options.resource.folders,
      },
    };
  }

  return { global: true };
}
