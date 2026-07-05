import { OpenApiRefPattern } from '../openapi/ref-patterns.js';
import type { ComponentFieldMap } from '../components/component.types.js';
import type { SchemaComponentDefinition } from '../components/schemas/schema-component.types.js';
import type {
  EntityBackendFields,
  EntityConstraintDefinition,
  EntityConstraintRule,
  EntityDefinition,
  EntityFieldMetadata,
  EntityOwner,
  EntityRef,
  EntityRegistry,
  EntityRelation,
  EntityRelationRegistry,
} from '../entities/entity.types.js';
import type { ComponentRef } from '../refs/ref.types.js';
import type { ResourceBuilder } from '../resource/define-resource.js';
import type { VersionContract } from '../version/version-contract.types.js';
import { isRefUsage } from '../validation/ref-usage-guards.js';
import { isComponentRef } from '../validation/ref-guards.js';
import type { RefResolver } from './refs/ref-resolver.types.js';
import { compileRouteSchema } from './paths/compile-route-schema.js';
import { normalizeExtendWithInput } from './schemas/normalize-extend-with.js';

export interface CompiledEntityMetadata {
  readonly baseEntities?: Record<string, unknown>;
  readonly entities?: Record<string, Record<string, unknown>>;
}

export function compileEntityMetadata(contract: VersionContract, resolver: RefResolver): CompiledEntityMetadata {
  const context = createEntityMetadataContext(contract);
  const baseEntities = compileBaseEntities(contract.baseEntityComponents, resolver, context);
  const entities = compileConcreteEntities(contract, resolver, context);

  return {
    ...(Object.keys(baseEntities).length > 0 ? { baseEntities } : {}),
    ...(Object.keys(entities).length > 0 ? { entities } : {}),
  };
}

interface EntityMetadataContext {
  readonly contract: VersionContract;
  readonly entitiesByRefId: Map<string, EntityDefinition>;
}

function createEntityMetadataContext(contract: VersionContract): EntityMetadataContext {
  const entitiesByRefId = new Map<string, EntityDefinition>();

  for (const registry of contract.baseEntityComponents) {
    for (const definition of registry.definitions) {
      entitiesByRefId.set(definition.ref.id, definition);
    }
  }

  for (const registry of contract.entityComponents) {
    for (const definition of registry.definitions) {
      entitiesByRefId.set(definition.ref.id, definition);
    }
  }

  for (const resource of contract.resources) {
    for (const registry of resource.entityComponents) {
      for (const definition of registry.definitions) {
        entitiesByRefId.set(definition.ref.id, definition);
      }
    }
  }

  return { contract, entitiesByRefId };
}

function compileBaseEntities(
  registries: readonly EntityRegistry[],
  resolver: RefResolver,
  context: EntityMetadataContext,
): Record<string, unknown> {
  const output: Record<string, unknown> = {};

  for (const registry of registries) {
    for (const definition of registry.definitions) {
      if (definition.kind !== 'abstract') {
        throw new Error(`Base entity registry "${registry.name}" can only contain abstract entities.`);
      }

      output[definition.key] = compileEntity(definition, resolver, context, { includeResource: false, normalizeInherited: false });
    }
  }

  return output;
}

function compileConcreteEntities(
  contract: VersionContract,
  resolver: RefResolver,
  context: EntityMetadataContext,
): Record<string, Record<string, unknown>> {
  const output: Record<string, Record<string, unknown>> = {};

  for (const registry of contract.entityComponents) {
    mergeEntityRegistry(output, 'shared', registry, [], resolver, context);
  }

  for (const resource of contract.resources) {
    mergeResourceEntities(output, resource, resolver, context);
  }

  return output;
}

function mergeResourceEntities(
  output: Record<string, Record<string, unknown>>,
  resource: ResourceBuilder,
  resolver: RefResolver,
  context: EntityMetadataContext,
): void {
  const relations = resource.entityRelationComponents.flatMap((registry) => registry.definitions);

  for (const registry of resource.entityComponents) {
    mergeEntityRegistry(output, resource.context.alias, registry, relations, resolver, context);
  }
}

function mergeEntityRegistry(
  output: Record<string, Record<string, unknown>>,
  ownerKey: string,
  registry: EntityRegistry,
  relations: readonly EntityRelation[],
  resolver: RefResolver,
  context: EntityMetadataContext,
): void {
  const target = (output[ownerKey] ??= {});

  for (const definition of registry.definitions) {
    if (definition.kind !== 'entity') {
      throw new Error(`Concrete entity registry "${registry.name}" cannot contain abstract entity "${definition.key}".`);
    }

    target[definition.key] = compileEntity(definition, resolver, context, {
      includeResource: true,
      normalizeInherited: true,
      relations: relations.filter((relation) => relation.source === definition.key),
    });
  }
}

function compileEntity(
  definition: EntityDefinition,
  resolver: RefResolver,
  context: EntityMetadataContext,
  options: {
    readonly includeResource: boolean;
    readonly normalizeInherited: boolean;
    readonly relations?: readonly EntityRelation[];
  },
): Record<string, unknown> {
  validateEntityDefinition(definition, context);

  const schema = toSchemaRef(definition.schema.id, resolver);
  const fields = removeEmptyFieldMetadata(options.normalizeInherited ? resolveEffectiveFields(definition, context) : resolveOwnFields(definition, context));
  const backend = compileBackendFields(definition.backend, resolver);
  const relations = compileRelations(definition, options.relations ?? [], context);
  const constraints = compileConstraints(definition.constraints);

  return cleanObject({
    kind: definition.kind,
    ...(options.includeResource && 'resource' in definition.owner ? { resource: { $ref: resourceRef(definition.owner.resource.name) } } : {}),
    schema,
    ...(definition.extends ? { extends: compileEntityRef(definition.extends) } : {}),
    store: definition.store,
    ...(definition.kind === 'entity' ? { visibility: ['backend', 'storage'] } : {}),
    backend,
    fields,
    relations,
    constraints,
    info: definition.info,
  });
}

function validateEntityDefinition(definition: EntityDefinition, context: EntityMetadataContext): void {
  if (definition.kind === 'abstract' && definition.store) {
    throw new Error(`Abstract entity "${definition.key}" must not define store.`);
  }

  if (definition.kind === 'entity' && !definition.store) {
    throw new Error(`Concrete entity "${definition.key}" must define store.`);
  }

  const fieldNames = resolveEntityFieldNames(definition, context);

  for (const fieldKey of Object.keys(definition.fields)) {
    if (!fieldNames.has(fieldKey)) {
      throw new Error(`Entity "${definition.key}" field metadata references unknown field "${fieldKey}".`);
    }
  }

  for (const [constraintName, constraint] of Object.entries(definition.constraints ?? {})) {
    validateConstraintFields(definition.key, constraintName, constraint, fieldNames);
  }
}

function resolveEntityFieldNames(definition: EntityDefinition, context: EntityMetadataContext): Set<string> {
  return new Set([...resolveInheritedFieldNames(definition, context), ...getSchemaFieldKeysByRefId(definition.schema.id, context), ...Object.keys(definition.backend ?? {})]);
}

function resolveInheritedFieldNames(definition: EntityDefinition, context: EntityMetadataContext): string[] {
  if (!definition.extends) return [];
  const base = context.entitiesByRefId.get(definition.extends.id);
  if (!base) return [];
  return Array.from(resolveEntityFieldNames(base, context));
}

function resolveEffectiveFields(definition: EntityDefinition, context: EntityMetadataContext): Record<string, EntityFieldMetadata> {
  return mergeFieldMetadata(
    Object.fromEntries(getSchemaFieldKeysByRefId(definition.schema.id, context).map((key) => [key, {}])),
    Object.fromEntries(Object.keys(definition.backend ?? {}).map((key) => [key, backendFieldDefaults()])),
    resolveInheritedFieldMetadata(definition, context),
    definition.fields,
  );
}

function resolveOwnFields(definition: EntityDefinition, context: EntityMetadataContext): Record<string, EntityFieldMetadata> {
  return mergeFieldMetadata(
    Object.fromEntries(getSchemaFieldKeysByRefId(definition.schema.id, context).map((key) => [key, {}])),
    Object.fromEntries(Object.keys(definition.backend ?? {}).map((key) => [key, backendFieldDefaults()])),
    definition.fields,
  );
}

function mergeFieldMetadata(...groups: Array<Record<string, EntityFieldMetadata> | undefined>): Record<string, EntityFieldMetadata> {
  const merged: Record<string, EntityFieldMetadata> = {};

  for (const group of groups) {
    for (const [key, value] of Object.entries(group ?? {})) {
      merged[key] = {
        ...(merged[key] ?? {}),
        ...value,
      };
    }
  }

  return merged;
}

function removeEmptyFieldMetadata(fields: Record<string, EntityFieldMetadata>): Record<string, EntityFieldMetadata> | undefined {
  const meaningful = Object.fromEntries(Object.entries(fields).filter(([, metadata]) => Object.keys(metadata).length > 0));
  return Object.keys(meaningful).length > 0 ? meaningful : undefined;
}

function backendFieldDefaults(): EntityFieldMetadata {
  return {
    select: false,
    edit: false,
  };
}

function resolveInheritedFieldMetadata(definition: EntityDefinition, context: EntityMetadataContext): Record<string, EntityFieldMetadata> {
  if (!definition.extends) return {};
  const base = context.entitiesByRefId.get(definition.extends.id);
  if (!base) return {};

  return resolveEffectiveFields(base, context);
}

function compileBackendFields(backend: EntityBackendFields | undefined, resolver: RefResolver): Record<string, unknown> | undefined {
  if (!backend || Object.keys(backend).length === 0) return undefined;

  return Object.fromEntries(Object.entries(backend).map(([key, value]) => [key, compileRouteSchema(value, resolver)]));
}

function compileRelations(
  definition: EntityDefinition,
  relations: readonly EntityRelation[],
  context: EntityMetadataContext,
): Record<string, unknown> | undefined {
  if (relations.length === 0) return undefined;

  for (const relation of relations) {
    validateRelation(definition, relation, context);
  }

  return Object.fromEntries(
    relations.map((relation) => [
      relation.name,
      {
        cardinality: relation.cardinality,
        target: { $ref: entityRefPointer(relation.target) },
        local: relation.local,
        foreign: relation.foreign,
        onDelete: relation.onDelete,
      },
    ]),
  );
}

function validateRelation(definition: EntityDefinition, relation: EntityRelation, context: EntityMetadataContext): void {
  const sourceFields = resolveEntityFieldNames(definition, context);
  if (!sourceFields.has(relation.local)) {
    throw new Error(`Entity "${definition.key}" relation "${relation.name}" references unknown local field "${relation.local}".`);
  }

  const targetDefinition = context.entitiesByRefId.get(relation.target.id);
  if (!targetDefinition) {
    throw new Error(`Entity "${definition.key}" relation "${relation.name}" references unknown target entity "${relation.target.entityKey}".`);
  }

  const targetFields = resolveEntityFieldNames(targetDefinition, context);
  if (!targetFields.has(relation.foreign)) {
    throw new Error(`Entity "${definition.key}" relation "${relation.name}" references unknown foreign field "${relation.foreign}".`);
  }
}

function compileConstraints(constraints: Record<string, EntityConstraintDefinition> | undefined): Record<string, unknown> | undefined {
  if (!constraints || Object.keys(constraints).length === 0) return undefined;

  return Object.fromEntries(
    Object.entries(constraints).map(([name, constraint]) => [
      name,
      cleanObject({
        kind: constraint.kind,
        fields: constraint.fields,
        rule: constraint.rule ? serializeConstraintRule(constraint.rule) : undefined,
      }),
    ]),
  );
}

function serializeConstraintRule(rule: EntityConstraintRule): Record<string, unknown> {
  return Object.fromEntries(
    Object.entries(rule).map(([key, value]) => [
      key,
      Array.isArray(value)
        ? value.map((item) => (isConstraintRule(item) ? serializeConstraintRule(item) : item))
        : isConstraintRule(value)
          ? serializeConstraintRule(value)
          : value,
    ]),
  );
}

function validateConstraintFields(
  entityName: string,
  constraintName: string,
  constraint: EntityConstraintDefinition,
  fieldNames: ReadonlySet<string>,
): void {
  for (const field of constraint.fields ?? []) {
    if (!fieldNames.has(field)) {
      throw new Error(`Entity "${entityName}" constraint "${constraintName}" references unknown field "${field}".`);
    }
  }

  if (constraint.rule) {
    validateConstraintRuleFields(entityName, constraintName, constraint.rule, fieldNames);
  }
}

function validateConstraintRuleFields(
  entityName: string,
  constraintName: string,
  rule: EntityConstraintRule,
  fieldNames: ReadonlySet<string>,
): void {
  const field = rule.field;
  if (typeof field === 'string' && !fieldNames.has(field)) {
    throw new Error(`Entity "${entityName}" constraint "${constraintName}" references unknown field "${field}".`);
  }

  for (const value of Object.values(rule)) {
    if (isConstraintRule(value)) {
      validateConstraintRuleFields(entityName, constraintName, value, fieldNames);
    } else if (Array.isArray(value)) {
      for (const item of value) {
        if (isConstraintRule(item)) {
          validateConstraintRuleFields(entityName, constraintName, item, fieldNames);
        }
      }
    }
  }
}

function getSchemaFieldKeysByRefId(refId: string, context: EntityMetadataContext): readonly string[] {
  const definition = findSchemaDefinitionByRefId(refId, context.contract);
  if (!definition) return [];

  return Object.keys(resolveSchemaObjectFields(definition.value, context.contract) ?? {});
}

function findSchemaDefinitionByRefId(refId: string, contract: VersionContract): SchemaComponentDefinition | undefined {
  for (const registry of contract.schemaComponents) {
    for (const definition of registry.definitions) {
      if (registry.ref[definition.name]?.id === refId) return definition;
    }
  }

  for (const resource of contract.resources) {
    for (const registry of resource.schemaComponents) {
      for (const definition of registry.definitions) {
        if (registry.ref[definition.name]?.id === refId) return definition;
      }
    }
  }

  return undefined;
}

function resolveSchemaObjectFields(value: unknown, contract: VersionContract): ComponentFieldMap | undefined {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return undefined;

  if (isRefUsage(value) && isComponentRef(value.ref)) {
    const baseDefinition = findSchemaDefinitionByRefId(value.ref.id, contract);
    const baseFields = resolveSchemaObjectFields(baseDefinition?.value, contract) ?? {};
    const extensionFields = normalizeExtendWithInput(value.usage.extendWith);

    return {
      ...baseFields,
      ...(extensionFields ?? {}),
    };
  }

  if (isComponentRef(value)) {
    const targetDefinition = findSchemaDefinitionByRefId(value.id, contract);
    return resolveSchemaObjectFields(targetDefinition?.value, contract);
  }

  if ('kind' in value || 'ref' in value) return undefined;

  return value as ComponentFieldMap;
}

function compileEntityRef(ref: EntityRef): Record<string, unknown> {
  return {
    owner: ref.owner,
    key: ref.entityKey,
  };
}

function entityRefPointer(ref: EntityRef): string {
  if ('resource' in ref.owner) return `#/x-codegen/entities/${ref.owner.resource.name}/${ref.entityKey}`;
  if (ref.abstract) return `#/x-codegen/baseEntities/${ref.entityKey}`;
  return `#/x-codegen/entities/shared/${ref.entityKey}`;
}

function resourceRef(resourceKey: string): string {
  return `#/x-codegen/resources/${resourceKey}`;
}

function toSchemaRef(refId: string, resolver: RefResolver): { readonly $ref: string } {
  const schemaName = resolver.schemas.get(refId);
  if (!schemaName) {
    throw new Error(`Unable to resolve entity schema ref: ${refId}`);
  }

  return {
    $ref: `${OpenApiRefPattern.schemas}${schemaName}`,
  };
}

function isConstraintRule(value: unknown): value is EntityConstraintRule {
  return !!value && typeof value === 'object' && !Array.isArray(value) && typeof (value as { op?: unknown }).op === 'string';
}

function cleanObject(input: Record<string, unknown>): Record<string, unknown> {
  return Object.fromEntries(
    Object.entries(input).filter(([, value]) => {
      if (value === undefined) return false;
      if (value && typeof value === 'object' && !Array.isArray(value) && Object.keys(value).length === 0) return false;
      return true;
    }),
  );
}
