// ─── codepurify/fields/check.ts ─────────────────────────────────────────────────

import type { FieldConfig } from './base';

// ─── Check rules ─────────────────────────────────────────────────────────────

export type Primitive = string | number | boolean;

export type FieldOperand = {
  field: () => FieldConfig;
};

export type RuleValue = Primitive | FieldOperand;

export interface FieldRef {
  field: () => FieldConfig;
}

// Rule interfaces
export interface EqRule {
  type: 'eq';
  field: FieldOperand;
  value: RuleValue;
}

export interface NeqRule {
  type: 'neq';
  field: FieldOperand;
  value: RuleValue;
}

export interface EmptyRule {
  type: 'empty';
  field: FieldOperand;
}

export interface NotEmptyRule {
  type: 'notEmpty';
  field: FieldOperand;
}

export interface InRule {
  type: 'in';
  field: FieldOperand;
  values: readonly (string | number | boolean)[];
}

export interface NotInRule {
  type: 'notIn';
  field: FieldOperand;
  values: readonly (string | number | boolean)[];
}

export interface RegexRule {
  type: 'regex';
  field: FieldOperand;
  pattern: string;
}

export interface GtRule {
  type: 'gt';
  field: FieldOperand;
  value: RuleValue;
}

export interface GteRule {
  type: 'gte';
  field: FieldOperand;
  value: RuleValue;
}

export interface LtRule {
  type: 'lt';
  field: FieldOperand;
  value: RuleValue;
}

export interface LteRule {
  type: 'lte';
  field: FieldOperand;
  value: RuleValue;
}

export interface IsNullRule {
  type: 'isNull';
  field: FieldOperand;
}

export interface IsNotNullRule {
  type: 'isNotNull';
  field: FieldOperand;
}

export interface NotRule {
  type: 'not';
  rule: CheckRule;
}

export interface AndRule {
  type: 'and';
  rules: readonly CheckRule[];
}

export interface OrRule {
  type: 'or';
  rules: readonly CheckRule[];
}

export type CheckRule =
  | EqRule
  | NeqRule
  | EmptyRule
  | NotEmptyRule
  | InRule
  | NotInRule
  | RegexRule
  | GtRule
  | GteRule
  | LtRule
  | LteRule
  | IsNullRule
  | IsNotNullRule
  | NotRule
  | AndRule
  | OrRule;

// ─── Check config ─────────────────────────────────────────────────────────────

export interface CheckConfig {
  name: string;
  rule: CheckRule;
}
