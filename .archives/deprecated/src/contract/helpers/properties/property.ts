import {
  FieldVisibilityLevel,
  FieldPersistenceMode,
  QueryOperator,
  PrimitiveFormat,
  PrimitiveType,
  type FieldCapabilityConfig,
  type FieldLifecycleConfig,
  type FieldPersistenceConfig,
  type FieldVisibilityConfig,
} from '@/contract/types/authoring/4.properties-builder';

import type {
  CapabilityHelper,
  CapabilityOptionsBuilder,
  LifecycleHelper,
  LifecycleOptionsBuilder,
  VisibilityHelper,
  VisibilityOptionsBuilder,
  CompositePropertyBuilder,
  CompositePropertySourceInput,
  EntityFieldInput,
  EntityFieldInputMap,
  EntityFieldOptions,
  EntityFieldSetOverrideBuilder,
  EntityFieldSetOverrideInput,
  EntityModelOverrideBuilder,
  EntityModelOverrideInput,
  EntityFieldSourceInput,
  EntityRelationKind,
  EntityTargetInput,
  FieldHelper,
  FieldSourceValue,
  NumberPropertyBuilder,
  PersistenceHelper,
  PersistenceOptionsBuilder,
  PrimitivePropertyBuilder,
  PrimitivePropertySourceInput,
  PropertyFieldBuilder,
  PropertyHelper,
  PropertySourceInputLike,
  QueryOperatorBuilder,
  RefPropertyBuilder,
  RefPropertySourceInput,
  RelationFieldBuilder,
  RelationInverseInput,
  ResolvedEntityTargetInput,
  UnresolvedRelationFieldSourceInput,
  EntityRelationLinkBuilder,
  EntityRelationOverrideFactory,
  StringPropertyBuilder,
  EnumPropertyBuilder,
  EnumPropertySourceInput,
  RelationFieldSourceInput,
} from '@/contract/types/authoring/4.properties-builder';

import { PropertySlotSourceMode, EntityRelationKind as RelationKind } from '@/contract/types/authoring/4.properties-builder';

import type {
  CompositeAuthoringRef,
  EntityFieldAuthoringRef,
  ModelAuthoringRef,
  PropertyAuthoringRef,
} from '@/contract/types/authoring/3.authoring-ref';

import { normalizeEntityTarget, resolveEntityTarget } from '@/contract/helpers/refs/normalize-authoring-ref';

import type { AnyEntityResult } from '@/contract/types/authoring/4.properties-builder';

// ============================================================================
// PROPERTY SOURCE HELPERS
// ============================================================================

function primitiveInput(type: PrimitiveType, format?: PrimitiveFormat): PrimitivePropertySourceInput {
  return {
    kind: 'primitive',
    type,
    ...(format === undefined ? {} : { format }),
  };
}

function patchPrimitive(input: PrimitivePropertySourceInput, patch: Partial<PrimitivePropertySourceInput>): PrimitivePropertySourceInput {
  return {
    ...input,
    ...patch,
    validation:
      input.validation || patch.validation
        ? {
            ...(input.validation ?? {}),
            ...(patch.validation ?? {}),
          }
        : undefined,
  };
}

function primitiveBuilder(input: PrimitivePropertySourceInput): PrimitivePropertyBuilder {
  return {
    input,

    min(value) {
      return primitiveBuilder(patchPrimitive(input, { validation: { minimum: value } }));
    },

    max(value) {
      return primitiveBuilder(patchPrimitive(input, { validation: { maximum: value } }));
    },

    exclusiveMin(value) {
      return primitiveBuilder(patchPrimitive(input, { validation: { exclusiveMinimum: value } }));
    },

    exclusiveMax(value) {
      return primitiveBuilder(patchPrimitive(input, { validation: { exclusiveMaximum: value } }));
    },

    multipleOf(value) {
      return primitiveBuilder(patchPrimitive(input, { validation: { multipleOf: value } }));
    },

    minLength(value) {
      return primitiveBuilder(patchPrimitive(input, { validation: { minLength: value } }));
    },

    maxLength(value) {
      return primitiveBuilder(patchPrimitive(input, { validation: { maxLength: value } }));
    },

    pattern(value) {
      return primitiveBuilder(patchPrimitive(input, { validation: { pattern: value } }));
    },

    format(value) {
      return primitiveBuilder(patchPrimitive(input, { format: value }));
    },

    example(value) {
      return primitiveBuilder(patchPrimitive(input, { example: value }));
    },

    description(value) {
      return primitiveBuilder({ ...input, description: value });
    },

    deprecated(value = true) {
      return primitiveBuilder({ ...input, deprecated: value });
    },

    meta(value) {
      return primitiveBuilder({ ...input, meta: value });
    },
  };
}

function stringBuilder(input: PrimitivePropertySourceInput): StringPropertyBuilder {
  const base = primitiveBuilder(input);

  return {
    ...base,

    email() {
      return stringBuilder(patchPrimitive(input, { format: PrimitiveFormat.email }));
    },

    uri() {
      return stringBuilder(patchPrimitive(input, { format: PrimitiveFormat.uri }));
    },

    url() {
      return stringBuilder(patchPrimitive(input, { format: PrimitiveFormat.url }));
    },

    uuid() {
      return stringBuilder(patchPrimitive(input, { format: PrimitiveFormat.uuid }));
    },

    objectId() {
      return stringBuilder(patchPrimitive(input, { format: PrimitiveFormat.objectId }));
    },

    phone() {
      return stringBuilder(patchPrimitive(input, { format: PrimitiveFormat.phone }));
    },

    password() {
      return stringBuilder(patchPrimitive(input, { format: PrimitiveFormat.password }));
    },

    date() {
      return stringBuilder(patchPrimitive(input, { format: PrimitiveFormat.date }));
    },

    dateTime() {
      return stringBuilder(patchPrimitive(input, { format: PrimitiveFormat.dateTime }));
    },

    time() {
      return stringBuilder(patchPrimitive(input, { format: PrimitiveFormat.time }));
    },

    binary() {
      return stringBuilder(patchPrimitive(input, { format: PrimitiveFormat.binary }));
    },
  };
}

function numberBuilder(input: PrimitivePropertySourceInput): NumberPropertyBuilder {
  const base = primitiveBuilder(input);

  return {
    ...base,

    int() {
      return numberBuilder(patchPrimitive(input, { type: PrimitiveType.integer }));
    },
  };
}

function enumBuilder(input: EnumPropertySourceInput): EnumPropertyBuilder {
  return {
    input,

    description(value) {
      return enumBuilder({ ...input, description: value });
    },

    deprecated(value = true) {
      return enumBuilder({ ...input, deprecated: value });
    },

    meta(value) {
      return enumBuilder({ ...input, meta: value });
    },
  };
}

function compositeBuilder(input: CompositePropertySourceInput): CompositePropertyBuilder {
  return {
    input,

    extends(ref: CompositeAuthoringRef) {
      return compositeBuilder({ ...input, extends: ref });
    },

    description(value) {
      return compositeBuilder({ ...input, description: value });
    },

    deprecated(value = true) {
      return compositeBuilder({ ...input, deprecated: value });
    },

    meta(value) {
      return compositeBuilder({ ...input, meta: value });
    },
  };
}

function refBuilder(input: RefPropertySourceInput): RefPropertyBuilder {
  return {
    input,

    description(value) {
      return refBuilder({ ...input, description: value });
    },

    deprecated(value = true) {
      return refBuilder({ ...input, deprecated: value });
    },

    meta(value) {
      return refBuilder({ ...input, meta: value });
    },
  };
}

// ============================================================================
// PROPERTY HELPER
// ============================================================================

export const property: PropertyHelper = {
  primitive(type) {
    return primitiveBuilder(primitiveInput(type));
  },

  string() {
    return stringBuilder(primitiveInput(PrimitiveType.string));
  },

  number() {
    return numberBuilder(primitiveInput(PrimitiveType.number));
  },

  integer() {
    return numberBuilder(primitiveInput(PrimitiveType.integer));
  },

  boolean() {
    return primitiveBuilder(primitiveInput(PrimitiveType.boolean));
  },

  date() {
    return stringBuilder(primitiveInput(PrimitiveType.string, PrimitiveFormat.date));
  },

  dateTime() {
    return stringBuilder(primitiveInput(PrimitiveType.string, PrimitiveFormat.dateTime));
  },

  time() {
    return stringBuilder(primitiveInput(PrimitiveType.string, PrimitiveFormat.time));
  },

  email() {
    return stringBuilder(primitiveInput(PrimitiveType.string, PrimitiveFormat.email));
  },

  uri() {
    return stringBuilder(primitiveInput(PrimitiveType.string, PrimitiveFormat.uri));
  },

  url() {
    return stringBuilder(primitiveInput(PrimitiveType.string, PrimitiveFormat.url));
  },

  uuid() {
    return stringBuilder(primitiveInput(PrimitiveType.string, PrimitiveFormat.uuid));
  },

  objectId() {
    return stringBuilder(primitiveInput(PrimitiveType.string, PrimitiveFormat.objectId));
  },

  phone() {
    return stringBuilder(primitiveInput(PrimitiveType.string, PrimitiveFormat.phone));
  },

  password() {
    return stringBuilder(primitiveInput(PrimitiveType.string, PrimitiveFormat.password));
  },

  binary() {
    return stringBuilder(primitiveInput(PrimitiveType.string, PrimitiveFormat.binary));
  },

  enum(values) {
    return enumBuilder({
      kind: 'enum',
      values,
    });
  },

  composite(properties) {
    return compositeBuilder({
      kind: 'composite',
      properties,
    });
  },

  ref(ref: PropertyAuthoringRef) {
    return refBuilder({
      kind: 'ref',
      ref,
    });
  },
};

// ============================================================================
// QUERY / ACCESS / PERSISTENCE HELPERS
// ============================================================================

function queryOperatorBuilder(values: readonly QueryOperator[] = []): QueryOperatorBuilder {
  const add = (value: QueryOperator) => queryOperatorBuilder([...values, value]);

  return {
    input: values,

    eq: () => add(QueryOperator.eq),
    neq: () => add(QueryOperator.neq),
    in: () => add(QueryOperator.in),
    notIn: () => add(QueryOperator.notIn),
    contains: () => add(QueryOperator.contains),
    startsWith: () => add(QueryOperator.startsWith),
    endsWith: () => add(QueryOperator.endsWith),
    gt: () => add(QueryOperator.gt),
    gte: () => add(QueryOperator.gte),
    lt: () => add(QueryOperator.lt),
    lte: () => add(QueryOperator.lte),
    between: () => add(QueryOperator.between),
    exists: () => add(QueryOperator.exists),
  };
}

function capabilityOptionsBuilder(config: FieldCapabilityConfig = {}): CapabilityOptionsBuilder {
  return {
    input: config,

    filter(value = true) {
      return capabilityOptionsBuilder({ ...config, filter: value });
    },

    sort(value = true) {
      return capabilityOptionsBuilder({ ...config, sort: value });
    },

    select(value = true) {
      return capabilityOptionsBuilder({ ...config, select: value });
    },

    operators(build) {
      return capabilityOptionsBuilder({
        ...config,
        operators: build(queryOperatorBuilder()).input,
      });
    },
  };
}

export const capability: CapabilityHelper = {
  operators() {
    return queryOperatorBuilder();
  },

  filter(value = true) {
    return capabilityOptionsBuilder().filter(value);
  },

  sort(value = true) {
    return capabilityOptionsBuilder().sort(value);
  },

  select(value = true) {
    return capabilityOptionsBuilder().select(value);
  },

  options(config) {
    return capabilityOptionsBuilder(config);
  },
};

function visibilityOptionsBuilder(config: FieldVisibilityConfig = {}): VisibilityOptionsBuilder {
  return {
    input: config,

    read(level) {
      return visibilityOptionsBuilder({ ...config, read: level });
    },

    write(level) {
      return visibilityOptionsBuilder({ ...config, write: level });
    },

    public() {
      return visibilityOptionsBuilder({ ...config, read: FieldVisibilityLevel.public });
    },

    internal() {
      return visibilityOptionsBuilder({ ...config, read: FieldVisibilityLevel.internal });
    },

    secret() {
      return visibilityOptionsBuilder({
        ...config,
        read: FieldVisibilityLevel.secret,
        sensitive: true,
      });
    },

    auth() {
      return visibilityOptionsBuilder({ ...config, read: FieldVisibilityLevel.auth });
    },

    sensitive(value = true) {
      return visibilityOptionsBuilder({ ...config, sensitive: value });
    },
  };
}

export const visibility: VisibilityHelper = {
  read(level) {
    return visibilityOptionsBuilder().read(level);
  },

  write(level) {
    return visibilityOptionsBuilder().write(level);
  },

  public() {
    return visibilityOptionsBuilder().public();
  },

  internal() {
    return visibilityOptionsBuilder().internal();
  },

  secret() {
    return visibilityOptionsBuilder().secret();
  },

  auth() {
    return visibilityOptionsBuilder().auth();
  },

  sensitive(value = true) {
    return visibilityOptionsBuilder().sensitive(value);
  },

  options(config) {
    return visibilityOptionsBuilder(config);
  },
};

function lifecycleOptionsBuilder(config: FieldLifecycleConfig = {}): LifecycleOptionsBuilder {
  return {
    input: config,

    create(value = true) {
      return lifecycleOptionsBuilder({ ...config, create: value });
    },

    update(value = true) {
      return lifecycleOptionsBuilder({ ...config, update: value });
    },

    immutable(value = true) {
      return lifecycleOptionsBuilder({ ...config, immutable: value });
    },

    generated(value = true) {
      return lifecycleOptionsBuilder({ ...config, generated: value });
    },

    readOnly(value = true) {
      return lifecycleOptionsBuilder({ ...config, readOnly: value });
    },
  };
}

export const lifecycle: LifecycleHelper = {
  create(value = true) {
    return lifecycleOptionsBuilder().create(value);
  },

  update(value = true) {
    return lifecycleOptionsBuilder().update(value);
  },

  immutable(value = true) {
    return lifecycleOptionsBuilder().immutable(value);
  },

  generated(value = true) {
    return lifecycleOptionsBuilder().generated(value);
  },

  readOnly(value = true) {
    return lifecycleOptionsBuilder().readOnly(value);
  },

  options(config) {
    return lifecycleOptionsBuilder(config);
  },
};

function persistenceOptionsBuilder(
  config: FieldPersistenceConfig = {
    mode: FieldPersistenceMode.stored,
  },
): PersistenceOptionsBuilder {
  return {
    input: config,

    mode(mode) {
      return persistenceOptionsBuilder({ ...config, mode });
    },

    stored() {
      return persistenceOptionsBuilder({
        ...config,
        mode: FieldPersistenceMode.stored,
      });
    },

    virtual() {
      return persistenceOptionsBuilder({
        ...config,
        mode: FieldPersistenceMode.virtual,
      });
    },

    computed() {
      return persistenceOptionsBuilder({
        ...config,
        mode: FieldPersistenceMode.computed,
      });
    },

    generated(value = true) {
      return persistenceOptionsBuilder({ ...config, generated: value });
    },

    immutable(value = true) {
      return persistenceOptionsBuilder({ ...config, immutable: value });
    },
  };
}

export const persistence: PersistenceHelper = {
  mode(mode) {
    return persistenceOptionsBuilder().mode(mode);
  },

  stored() {
    return persistenceOptionsBuilder().stored();
  },

  virtual() {
    return persistenceOptionsBuilder().virtual();
  },

  computed() {
    return persistenceOptionsBuilder().computed();
  },

  generated(value = true) {
    return persistenceOptionsBuilder().generated(value);
  },

  immutable(value = true) {
    return persistenceOptionsBuilder().immutable(value);
  },

  options(config) {
    return persistenceOptionsBuilder(config);
  },
};

// ============================================================================
// FIELD HELPERS
// ============================================================================

function fieldInput(source: EntityFieldInput['source'], options?: EntityFieldOptions): EntityFieldInput {
  return {
    source,
    ...(options === undefined ? {} : { options }),
  };
}

function patchField(input: EntityFieldInput, patch: EntityFieldOptions): EntityFieldInput {
  return {
    ...input,
    options: {
      ...(input.options ?? {}),
      ...patch,
    },
  };
}

function propertyFieldBuilder(input: EntityFieldInput): PropertyFieldBuilder {
  return {
    input,

    required(value = true) {
      return propertyFieldBuilder(patchField(input, { required: value }));
    },

    optional() {
      return propertyFieldBuilder(patchField(input, { required: false }));
    },

    nullable(value = true) {
      return propertyFieldBuilder(patchField(input, { nullable: value }));
    },

    nonNullable() {
      return propertyFieldBuilder(patchField(input, { nullable: false }));
    },

    array(options = true) {
      return propertyFieldBuilder(patchField(input, { array: options }));
    },

    single() {
      return propertyFieldBuilder(patchField(input, { array: false }));
    },

    default(value) {
      return propertyFieldBuilder(patchField(input, { default: value }));
    },

    capability(build) {
      return propertyFieldBuilder(patchField(input, { capability: build(capability).input }));
    },

    visibility(build) {
      return propertyFieldBuilder(patchField(input, { visibility: build(visibility).input }));
    },

    lifecycle(build) {
      return propertyFieldBuilder(patchField(input, { lifecycle: build(lifecycle).input }));
    },

    persistence(build) {
      return propertyFieldBuilder(patchField(input, { persistence: build(persistence).input }));
    },

    description(value) {
      return propertyFieldBuilder(patchField(input, { description: value }));
    },

    deprecated(value = true) {
      return propertyFieldBuilder(patchField(input, { deprecated: value }));
    },

    meta(value) {
      return propertyFieldBuilder(patchField(input, { meta: value }));
    },
  };
}

function fieldFromValue(source: FieldSourceValue): PropertyFieldBuilder {
  if ('kind' in source && source.kind.includes('property.')) {
    return propertyFieldBuilder(
      fieldInput({
        mode: PropertySlotSourceMode.ref,
        ref: source as PropertyAuthoringRef,
      }),
    );
  }

  if ('kind' in source && source.kind === 'schema.model') {
    return propertyFieldBuilder(
      fieldInput({
        mode: PropertySlotSourceMode.ref,
        ref: source as ModelAuthoringRef,
      }),
    );
  }

  return propertyFieldBuilder(
    fieldInput({
      mode: PropertySlotSourceMode.inline,
      property: source as PropertySourceInputLike,
    } as unknown as EntityFieldSourceInput),
  );
}

function inlinePropertyField(source: PropertySourceInputLike): PropertyFieldBuilder {
  return propertyFieldBuilder(
    fieldInput({
      mode: PropertySlotSourceMode.inline,
      property: source,
    } as unknown as EntityFieldSourceInput),
  );
}

function patchRelationSource(input: EntityFieldInput, patch: Partial<RelationFieldSourceInput>): EntityFieldInput {
  if (input.source.mode !== PropertySlotSourceMode.relation) {
    return input;
  }

  const nextSource = {
    ...input.source,
    ...patch,
  };

  if (nextSource.relation !== undefined && nextSource.target !== undefined) {
    return {
      ...input,
      source: nextSource as RelationFieldSourceInput,
    };
  }

  return {
    ...input,
    source: nextSource as UnresolvedRelationFieldSourceInput,
  };
}
function resolveRelationCallbackTarget(target: EntityTargetInput): ResolvedEntityTargetInput {
  return resolveEntityTarget(target);
}

function resolveRelationInverse(target: EntityTargetInput, refOrFactory: RelationInverseInput): EntityFieldAuthoringRef {
  if (typeof refOrFactory !== 'function') {
    return refOrFactory;
  }

  const resolvedTarget = resolveRelationCallbackTarget(target);

  return refOrFactory(resolvedTarget as AnyEntityResult);
}

function resolveRelationThroughMapping(
  entity: EntityTargetInput,
  map?: (join: any) => {
    readonly from: EntityFieldAuthoringRef;
    readonly to: EntityFieldAuthoringRef;
  },
) {
  if (!map) {
    return undefined;
  }

  return {
    entity,
    map,
  };
}

function relationFieldBuilder(input: EntityFieldInput): RelationFieldBuilder {
  return {
    input,

    required(value = true) {
      return relationFieldBuilder(patchField(input, { required: value }));
    },

    optional() {
      return relationFieldBuilder(patchField(input, { required: false }));
    },

    nullable(value = true) {
      return relationFieldBuilder(patchField(input, { nullable: value }));
    },

    nonNullable() {
      return relationFieldBuilder(patchField(input, { nullable: false }));
    },

    array(options = true) {
      return relationFieldBuilder(patchField(input, { array: options }));
    },

    single() {
      return relationFieldBuilder(patchField(input, { array: false }));
    },

    default(value) {
      return relationFieldBuilder(patchField(input, { default: value }));
    },

    capability(build) {
      return relationFieldBuilder(patchField(input, { capability: build(capability).input }));
    },

    visibility(build) {
      return relationFieldBuilder(patchField(input, { visibility: build(visibility).input }));
    },

    lifecycle(build) {
      return relationFieldBuilder(patchField(input, { lifecycle: build(lifecycle).input }));
    },

    persistence(build) {
      return relationFieldBuilder(patchField(input, { persistence: build(persistence).input }));
    },

    inverse(refOrFactory) {
      if (input.source.mode !== PropertySlotSourceMode.relation) {
        return relationFieldBuilder(input);
      }

      if (!input.source.target) {
        return relationFieldBuilder(input);
      }

      return relationFieldBuilder(
        patchRelationSource(input, {
          inverse: resolveRelationInverse(input.source.target, refOrFactory),
        }),
      );
    },

    through(entity, map) {
      return relationFieldBuilder(
        patchRelationSource(input, {
          through: {
            entity: normalizeEntityTarget(entity),
            from: map.from,
            to: map.to,
          },
        }),
      );
    },

    expandable(value = true) {
      return relationFieldBuilder(patchRelationSource(input, { expandable: value }));
    },

    relationName(name) {
      return relationFieldBuilder(patchRelationSource(input, { relationName: name }));
    },

    description(value) {
      return relationFieldBuilder(patchField(input, { description: value }));
    },

    deprecated(value = true) {
      return relationFieldBuilder(patchField(input, { deprecated: value }));
    },

    meta(value) {
      return relationFieldBuilder(patchField(input, { meta: value }));
    },
  };
}

function relationField(relation: EntityRelationKind, target: EntityTargetInput): RelationFieldBuilder {
  return relationFieldBuilder(
    fieldInput({
      mode: PropertySlotSourceMode.relation,
      relation,
      target,
    }),
  );
}

function relationSlotField(): RelationFieldBuilder {
  return relationFieldBuilder(
    fieldInput({
      mode: PropertySlotSourceMode.relation,
    }),
  );
}

export function entityRelationLinkBuilder(base: EntityFieldInput): EntityRelationLinkBuilder {
  function link(relation: EntityRelationKind, target: EntityTargetInput): RelationFieldBuilder {
    return relationFieldBuilder({
      ...base,
      source: {
        ...(base.source.mode === PropertySlotSourceMode.relation ? base.source : {}),
        mode: PropertySlotSourceMode.relation,
        relation,
        target,
      },
    });
  }

  return {
    belongsTo(target) {
      return link(RelationKind.belongsTo, target);
    },

    hasOne(target) {
      return link(RelationKind.hasOne, target);
    },

    hasMany(target) {
      return link(RelationKind.hasMany, target);
    },

    manyToMany(target) {
      return link(RelationKind.manyToMany, target);
    },
  };
}

const callableField = ((source: FieldSourceValue) => fieldFromValue(source)) as FieldHelper;

callableField.from = fieldFromValue;

callableField.primitive = (type) => inlinePropertyField(property.primitive(type));
callableField.string = () => inlinePropertyField(property.string());
callableField.number = () => inlinePropertyField(property.number());
callableField.integer = () => inlinePropertyField(property.integer());
callableField.boolean = () => inlinePropertyField(property.boolean());
callableField.date = () => inlinePropertyField(property.date());
callableField.dateTime = () => inlinePropertyField(property.dateTime());
callableField.time = () => inlinePropertyField(property.time());
callableField.email = () => inlinePropertyField(property.email());
callableField.uri = () => inlinePropertyField(property.uri());
callableField.url = () => inlinePropertyField(property.url());
callableField.uuid = () => inlinePropertyField(property.uuid());
callableField.objectId = () => inlinePropertyField(property.objectId());
callableField.phone = () => inlinePropertyField(property.phone());
callableField.password = () => inlinePropertyField(property.password());
callableField.binary = () => inlinePropertyField(property.binary());

callableField.enum = (values) => inlinePropertyField(property.enum(values));
callableField.composite = (properties) => inlinePropertyField(property.composite(properties));

callableField.ref = (ref) => callableField(ref);

callableField.relation = relationSlotField;

callableField.belongsTo = (target) => relationField(RelationKind.belongsTo, target);
callableField.hasOne = (target) => relationField(RelationKind.hasOne, target);
callableField.hasMany = (target) => relationField(RelationKind.hasMany, target);
callableField.manyToMany = (target) => relationField(RelationKind.manyToMany, target);

export const field = callableField;

// ============================================================================
// MODEL / FIELD SET OVERRIDE HELPERS
// ============================================================================

export function entityModelOverrideBuilder<TFields extends EntityFieldInputMap>(
  input: EntityModelOverrideInput<TFields> = {},
): EntityModelOverrideBuilder<TFields> {
  return {
    input,

    pick(...fields) {
      return entityModelOverrideBuilder<TFields>({
        ...input,
        pick: fields,
      });
    },

    omit(...fields) {
      return entityModelOverrideBuilder<TFields>({
        ...input,
        omit: fields,
      });
    },

    partial(value = true) {
      return entityModelOverrideBuilder<TFields>({
        ...input,
        partial: value,
      });
    },

    relations(shape) {
      return entityModelOverrideBuilder<TFields>({
        ...input,
        relations: shape,
      });
    },

    extendWith(fields) {
      return entityModelOverrideBuilder<TFields>({
        ...input,
        extendWith: fields,
      });
    },

    description(value) {
      return entityModelOverrideBuilder<TFields>({
        ...input,
        description: value,
      });
    },

    deprecated(value = true) {
      return entityModelOverrideBuilder<TFields>({
        ...input,
        deprecated: value,
      });
    },

    meta(value) {
      return entityModelOverrideBuilder<TFields>({
        ...input,
        meta: value,
      });
    },
  };
}

export function entityFieldSetOverrideBuilder<TFields extends EntityFieldInputMap>(
  input: EntityFieldSetOverrideInput<TFields> = {},
): EntityFieldSetOverrideBuilder<TFields> {
  return {
    input,

    only(...fields) {
      return entityFieldSetOverrideBuilder<TFields>({
        ...input,
        mode: 'only',
        fields,
      });
    },

    include(...fields) {
      return entityFieldSetOverrideBuilder<TFields>({
        ...input,
        mode: 'include',
        fields,
      });
    },

    exclude(...fields) {
      return entityFieldSetOverrideBuilder<TFields>({
        ...input,
        mode: 'exclude',
        fields,
      });
    },

    description(value) {
      return entityFieldSetOverrideBuilder<TFields>({
        ...input,
        description: value,
      });
    },

    deprecated(value = true) {
      return entityFieldSetOverrideBuilder<TFields>({
        ...input,
        deprecated: value,
      });
    },

    meta(value) {
      return entityFieldSetOverrideBuilder<TFields>({
        ...input,
        meta: value,
      });
    },
  };
}
