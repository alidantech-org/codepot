import { EngineIdPart, createEngineId } from '../core/engine-id';
import { normalizeInfo, ownerFromResource } from '../core/normalize';
import type {
  BaseEntityDefinitionInput,
  ConcreteEntityDefinitionInput,
  DefineEntitiesOptions,
  EntityConstraintBuilder,
  EntityConstraintDefinition,
  EntityConstraintRule,
  EntityConstraintValue,
  EntityDefinition,
  EntityDefinitionFactory,
  EntityDefinitionInput,
  EntityFieldBuilder,
  EntityFieldMetadata,
  EntityFieldQueryBuilder,
  EntityFieldQueryMetadata,
  EntityFieldRole,
  EntityGeneratedStrategy,
  EntityRef,
  EntityRegistry,
  EntityRelationBuilder,
  EntityRelationCardinality,
  EntityRelationDeleteBehavior,
  EntityRelationRef,
  EntityRelationRegistry,
  EntityRelationsInput,
  EntitySearchQueryOptions,
} from './entity.types';

export function defineBaseEntities<const TInput extends Record<string, BaseEntityDefinitionInput>>(
  input: TInput | EntityDefinitionFactory<TInput>,
): EntityRegistry<TInput> {
  return defineEntitiesInternal({ name: 'shared' }, input, true);
}

export function defineEntities<const TInput extends Record<string, ConcreteEntityDefinitionInput>>(
  options: DefineEntitiesOptions,
  input: TInput | EntityDefinitionFactory<TInput>,
): EntityRegistry<TInput> {
  return defineEntitiesInternal(options, input, false);
}

function defineEntitiesInternal<TInput extends Record<string, EntityDefinitionInput>>(
  options: DefineEntitiesOptions,
  input: TInput | EntityDefinitionFactory<TInput>,
  forceAbstract: boolean,
): EntityRegistry<TInput> {
  const owner = ownerFromResource(options.resource);
  const provisional = new Proxy<Record<string, EntityRef>>({}, {
    get: (_target, property: string) => createEntityRef(options, property, owner, forceAbstract),
  });
  const values = typeof input === 'function' ? input({ ref: provisional }) : input;
  const refs = Object.fromEntries(Object.entries(values).map(([key, value]) => [
    key,
    createEntityRef(options, key, owner, forceAbstract || value.kind === 'abstract'),
  ])) as EntityRegistry<TInput>['ref'];
  const definitions = Object.entries(values).map(([key, value]) => normalizeEntity(key, value, refs[key]!, owner));
  return { name: options.name, owner, abstract: forceAbstract, definitions, ref: refs };
}

export function defineEntityRelations(
  options: { readonly resource?: DefineEntitiesOptions['resource'] },
  input: EntityRelationsInput,
): EntityRelationRegistry {
  const owner = ownerFromResource(options.resource);
  const builder = new FluentEntityRelationBuilder();
  const definitions = Object.entries(input).flatMap(([source, relations]) => Object.entries(relations).map(([name, factory]) => {
    const relation = factory(builder);
    if (!relation.localField || !relation.foreignField) throw new Error(`Relation "${source}.${name}" requires local(...) and foreign(...).`);
    return {
      source,
      name,
      cardinality: relation.cardinality,
      target: relation.target,
      local: relation.localField,
      foreign: relation.foreignField,
      ...(relation.deleteBehavior ? { onDelete: relation.deleteBehavior } : {}),
    };
  }));
  return { owner, definitions };
}

function normalizeEntity(
  key: string,
  value: EntityDefinitionInput,
  ref: EntityRef,
  owner: EntityDefinition['owner'],
): EntityDefinition {
  const fields = Object.fromEntries(Object.entries(value.fields ?? {}).map(([name, factory]) => [name, factory(new FluentEntityFieldBuilder()).build()]));
  const constraints = 'constraints' in value && value.constraints
    ? value.constraints(new FluentEntityConstraintBuilder())
    : undefined;
  return {
    key,
    kind: value.kind === 'abstract' ? 'abstract' : 'entity',
    schema: value.schema,
    ...(value.extends ? { extends: value.extends } : {}),
    ...('store' in value ? { store: value.store } : {}),
    ...('backend' in value && value.backend ? { backend: value.backend } : {}),
    fields,
    ...(constraints ? { constraints } : {}),
    ...(value.info && normalizeInfo(value.info) ? { info: normalizeInfo(value.info)! } : {}),
    owner,
    ref,
  };
}

function createEntityRef(
  options: DefineEntitiesOptions,
  key: string,
  owner: EntityDefinition['owner'],
  abstract: boolean,
): EntityRef {
  const id = options.resource
    ? createEngineId(EngineIdPart.resource, options.resource.name, EngineIdPart.model, key)
    : createEngineId(EngineIdPart.model, key);
  return { id, name: key, kind: 'entity', entityKey: key, owner, abstract };
}

class FluentEntityFieldBuilder implements EntityFieldBuilder {
  #metadata: EntityFieldMetadata = {};
  index(): EntityFieldBuilder { this.#metadata = { ...this.#metadata, index: true }; return this; }
  unique(): EntityFieldBuilder { this.#metadata = { ...this.#metadata, unique: true }; return this; }
  readonly(): EntityFieldBuilder { this.#metadata = { ...this.#metadata, readonly: true }; return this; }
  managed(): EntityFieldBuilder { this.#metadata = { ...this.#metadata, managed: true, readonly: true }; return this; }
  immutable(): EntityFieldBuilder { this.#metadata = { ...this.#metadata, immutable: true }; return this; }
  select(_enabled: false): EntityFieldBuilder { this.#metadata = { ...this.#metadata, select: false }; return this; }
  edit(_enabled: false): EntityFieldBuilder { this.#metadata = { ...this.#metadata, edit: false }; return this; }
  role(role: EntityFieldRole): EntityFieldBuilder { this.#metadata = { ...this.#metadata, role }; return this; }
  generated(strategy: EntityGeneratedStrategy): EntityFieldBuilder { this.#metadata = { ...this.#metadata, generated: strategy, managed: true, readonly: true }; return this; }
  query(callback: (query: EntityFieldQueryBuilder) => EntityFieldQueryBuilder): EntityFieldBuilder { this.#metadata = { ...this.#metadata, query: callback(new FluentEntityFieldQueryBuilder()).build() }; return this; }
  info(info: import('../core/authoring.types').InfoInput): EntityFieldBuilder { const normalized = normalizeInfo(info); this.#metadata = normalized ? { ...this.#metadata, info: normalized } : this.#metadata; return this; }
  build(): EntityFieldMetadata { return { ...this.#metadata }; }
}
class FluentEntityFieldQueryBuilder implements EntityFieldQueryBuilder {
  #metadata: EntityFieldQueryMetadata = {};
  exact(): EntityFieldQueryBuilder { this.#metadata = { ...this.#metadata, exact: true }; return this; }
  oneOf(): EntityFieldQueryBuilder { this.#metadata = { ...this.#metadata, oneOf: true }; return this; }
  range(): EntityFieldQueryBuilder { this.#metadata = { ...this.#metadata, range: true }; return this; }
  date(): EntityFieldQueryBuilder { this.#metadata = { ...this.#metadata, date: true }; return this; }
  search(options: EntitySearchQueryOptions): EntityFieldQueryBuilder { this.#metadata = { ...this.#metadata, search: options }; return this; }
  sort(): EntityFieldQueryBuilder { this.#metadata = { ...this.#metadata, sort: true }; return this; }
  build(): EntityFieldQueryMetadata { return { ...this.#metadata }; }
}
class FluentEntityConstraintBuilder implements EntityConstraintBuilder {
  index(fields: readonly string[]): EntityConstraintDefinition { return { kind: 'index', fields: [...fields] }; }
  unique(fields: readonly string[]): EntityConstraintDefinition { return { kind: 'unique', fields: [...fields] }; }
  check(rule: EntityConstraintRule): EntityConstraintDefinition { return { kind: 'check', rule }; }
  gt(field: string, value: EntityConstraintValue): EntityConstraintRule { return { op: 'gt', field, value }; }
  gte(field: string, value: EntityConstraintValue): EntityConstraintRule { return { op: 'gte', field, value }; }
  lt(field: string, value: EntityConstraintValue): EntityConstraintRule { return { op: 'lt', field, value }; }
  lte(field: string, value: EntityConstraintValue): EntityConstraintRule { return { op: 'lte', field, value }; }
  eq(field: string, value: EntityConstraintValue): EntityConstraintRule { return { op: 'eq', field, value }; }
  neq(field: string, value: EntityConstraintValue): EntityConstraintRule { return { op: 'neq', field, value }; }
  notNull(field: string): EntityConstraintRule { return { op: 'notNull', field }; }
  oneOf(field: string, values: readonly EntityConstraintValue[]): EntityConstraintRule { return { op: 'oneOf', field, values }; }
  range(field: string, min: EntityConstraintValue, max: EntityConstraintValue): EntityConstraintRule { return { op: 'range', field, min, max }; }
  when(condition: EntityConstraintRule, thenCondition: EntityConstraintRule): EntityConstraintRule { return { op: 'when', condition, then: thenCondition }; }
  and(...conditions: EntityConstraintRule[]): EntityConstraintRule { return { op: 'and', conditions }; }
  or(...conditions: EntityConstraintRule[]): EntityConstraintRule { return { op: 'or', conditions }; }
  field(fieldName: string): { readonly $field: string } { return { $field: fieldName }; }
}
class FluentEntityRelationBuilder implements EntityRelationBuilder {
  belongsTo(target: EntityRef): EntityRelationRef { return createRelation('belongsTo', target); }
  hasOne(target: EntityRef): EntityRelationRef { return createRelation('hasOne', target); }
  hasMany(target: EntityRef): EntityRelationRef { return createRelation('hasMany', target); }
  manyToMany(target: EntityRef): EntityRelationRef { return createRelation('manyToMany', target); }
}
function createRelation(cardinality: EntityRelationCardinality, target: EntityRef): EntityRelationRef {
  let current: EntityRelationRef;
  const rebuild = (localField?: string, foreignField?: string, deleteBehavior?: EntityRelationDeleteBehavior): EntityRelationRef => {
    current = {
      cardinality,
      target,
      ...(localField ? { localField } : {}),
      ...(foreignField ? { foreignField } : {}),
      ...(deleteBehavior ? { deleteBehavior } : {}),
      local(field: string): EntityRelationRef { return rebuild(field, foreignField, deleteBehavior); },
      foreign(field: string): EntityRelationRef { return rebuild(localField, field, deleteBehavior); },
      onDelete(behavior: EntityRelationDeleteBehavior): EntityRelationRef { return rebuild(localField, foreignField, behavior); },
    };
    return current;
  };
  return rebuild();
}
