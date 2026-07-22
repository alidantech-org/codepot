// ─── codepurify/fields/factories.ts ─────────────────────────────────────────────────

import {
  StringFieldConfig,
  BooleanFieldConfig,
  EnumFieldConfig,
  UuidFieldConfig,
  ForeignFieldConfig,
  SecurityConfig,
  EqRule,
  NeqRule,
  EmptyRule,
  NotEmptyRule,
  InRule,
  NotInRule,
  RegexRule,
  GtRule,
  GteRule,
  LtRule,
  LteRule,
  IsNullRule,
  IsNotNullRule,
  FieldOperand,
  RuleValue,
  CheckRule,
  NotRule,
  AndRule,
  OrRule,
  RelationFieldConfig,
  RelationConfigUnion,
  IEntityConfig,
  EntityConfigClass,
} from '../types';

// ─── Field Rule Helpers ─────────────────────────────────────────────────────────

export function ref(fieldRef: () => any): FieldOperand {
  return {
    field: fieldRef,
  };
}

export function field(fieldRef: () => any) {
  return {
    eq(value: RuleValue): EqRule {
      return { type: 'eq', field: { field: fieldRef }, value };
    },
    neq(value: RuleValue): NeqRule {
      return { type: 'neq', field: { field: fieldRef }, value };
    },
    empty(): EmptyRule {
      return { type: 'empty', field: { field: fieldRef } };
    },
    notEmpty(): NotEmptyRule {
      return { type: 'notEmpty', field: { field: fieldRef } };
    },
    in(values: readonly (string | number | boolean)[]): InRule {
      return { type: 'in', field: { field: fieldRef }, values };
    },
    notIn(values: readonly (string | number | boolean)[]): NotInRule {
      return { type: 'notIn', field: { field: fieldRef }, values };
    },
    regex(pattern: string): RegexRule {
      return { type: 'regex', field: { field: fieldRef }, pattern };
    },
    gt(value: RuleValue): GtRule {
      return { type: 'gt', field: { field: fieldRef }, value };
    },
    gte(value: RuleValue): GteRule {
      return { type: 'gte', field: { field: fieldRef }, value };
    },
    lt(value: RuleValue): LtRule {
      return { type: 'lt', field: { field: fieldRef }, value };
    },
    lte(value: RuleValue): LteRule {
      return { type: 'lte', field: { field: fieldRef }, value };
    },
    isNull(): IsNullRule {
      return { type: 'isNull', field: { field: fieldRef } };
    },
    isNotNull(): IsNotNullRule {
      return { type: 'isNotNull', field: { field: fieldRef } };
    },
  };
}

// ─── Logical Helpers ─────────────────────────────────────────────────────────────

export function not(rule: CheckRule): NotRule {
  return { type: 'not', rule };
}

export function and(...rules: CheckRule[]): AndRule {
  return { type: 'and', rules };
}

export function or(...rules: CheckRule[]): OrRule {
  return { type: 'or', rules };
}

// ─── Query rule assertion ───────────────────────────────────────────────────────

function assertQueryRules(query?: any, security?: SecurityConfig): void {
  // Validate query configuration
  if (query) {
    // Check for valid query operations
    const validOperations = ['select', 'filter', 'sort', 'search', 'defaultSelect'];
    const queryOps = Object.keys(query);

    for (const op of queryOps) {
      if (!validOperations.includes(op)) {
        throw new Error(`Invalid query operation: ${op}. Valid operations are: ${validOperations.join(', ')}`);
      }
    }

    // Validate specific query configurations
    if (query.select !== undefined && typeof query.select !== 'boolean') {
      throw new Error('query.select must be a boolean');
    }

    if (query.filter !== undefined && typeof query.filter !== 'boolean') {
      throw new Error('query.filter must be a boolean');
    }

    if (query.sort !== undefined && typeof query.sort !== 'boolean') {
      throw new Error('query.sort must be a boolean');
    }

    if (query.search !== undefined && typeof query.search !== 'boolean') {
      throw new Error('query.search must be a boolean');
    }

    if (query.defaultSelect !== undefined && typeof query.defaultSelect !== 'boolean') {
      throw new Error('query.defaultSelect must be a boolean');
    }
  }

  // Validate security configuration
  if (security) {
    // Check for valid security properties
    const validSecurityProps = ['level'];
    const securityProps = Object.keys(security);

    for (const prop of securityProps) {
      if (!validSecurityProps.includes(prop)) {
        throw new Error(`Invalid security property: ${prop}. Valid properties are: ${validSecurityProps.join(', ')}`);
      }
    }

    // Validate security level
    const validSecurityLevels = ['public', 'internal', 'private', 'pii', 'secret'];
    if (security.level && !validSecurityLevels.includes(security.level)) {
      throw new Error(`Invalid security level: ${security.level}. Valid levels are: ${validSecurityLevels.join(', ')}`);
    }
  }
}

// ─── Field factories ──────────────────────────────────────────────────────────

export function stringField(config: Omit<StringFieldConfig, 'kind'>): StringFieldConfig {
  assertQueryRules(config.query, config.security);
  return {
    kind: 'string',
    ...config,
  };
}

export function booleanField(config: Omit<BooleanFieldConfig, 'kind'>): BooleanFieldConfig {
  assertQueryRules(config.query, config.security);
  return {
    kind: 'boolean',
    ...config,
  };
}

export function enumField<const T extends readonly string[]>(
  values: T,
  config: Omit<EnumFieldConfig<T[number]>, 'kind' | 'value_list' | 'values'> = {},
): EnumFieldConfig<T[number]> {
  assertQueryRules(config.query, config.security);

  // Helper function to create typed enum value map
  type EnumValueMap<T extends readonly string[]> = {
    readonly [K in T[number]]: K;
  };

  function makeEnumValueMap<const T extends readonly string[]>(values: T): EnumValueMap<T> {
    return Object.fromEntries(values.map((value) => [value, value])) as EnumValueMap<T>;
  }

  return {
    kind: 'enum',
    value_list: values,
    values: makeEnumValueMap(values),
    ...config,
  } as const;
}

export function uuidField(config: Omit<UuidFieldConfig, 'kind'>): UuidFieldConfig {
  assertQueryRules(config.query, config.security);
  return {
    kind: 'uuid',
    ...config,
  };
}

// ─── Foreign Field Factory ─────────────────────────────────────────────────────

export function foreignField<T extends IEntityConfig>(remoteConfig: T, config: Omit<ForeignFieldConfig, 'kind'>): ForeignFieldConfig {
  return {
    kind: 'foreign',
    ...config,
  };
}

// ─── Relation Field Factory ─────────────────────────────────────────────────────

export function relationField(
  localEntity: IEntityConfig,
  remoteEntity: EntityConfigClass,
  config: RelationFieldConfig,
): RelationConfigUnion {
  return config.relation;
}
