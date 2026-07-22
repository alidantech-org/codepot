// ─── codepurify/fields/base.ts ─────────────────────────────────────────────────

// ─── Actors ───────────────────────────────────────────────────────────────────

export type Actor = 'api' | 'system' | false;

// ─── Security ─────────────────────────────────────────────────────────────────--

export type SecurityLevel = 'public' | 'internal' | 'private' | 'pii' | 'secret';

export interface SecurityConfig {
  level: SecurityLevel;
}

// ─── Query ────────────────────────────────────────────────────────────────────

export interface QueryConfig {
  select?: boolean;
  defaultSelect?: boolean;
  sort?: boolean;
  search?: boolean;
  filter?: boolean;
  dateRange?: boolean;
}

// ─── Mutation ─────────────────────────────────────────────────────────────────

export interface MutationConfig {
  create?: Actor;
  update?: Actor;
  edit?: Actor;
  immutable?: boolean;
  immutable_after_create?: boolean;
  generated?: boolean;
  computed?: boolean;
  persisted?: boolean;
  required_on_create?: boolean;
  optional_on_create?: boolean;
  nullable_on_create?: boolean;
}

// ─── State ────────────────────────────────────────────────────────────────────

export interface ToggleState {
  toggle: true;
}

export interface TransitionState<S extends string> {
  transition: true;
  initial: S;
  terminal: readonly S[];
  transitions: Record<S, readonly S[]>;
}

// ─── Business / System ────────────────────────────────────────────────────────

export interface BusinessConfig {
  contextual?: boolean;
  contextKey?: string;
}

export interface SystemConfig {
  persisted?: boolean;
  computed?: boolean;
}

// ─── Base field ───────────────────────────────────────────────────────────────

export type FieldKind = 'string' | 'boolean' | 'enum' | 'uuid' | 'foreign';

export interface BaseFieldConfig {
  kind: FieldKind;
  nullable?: boolean;
  query?: QueryConfig;
  mutation?: MutationConfig;
  security?: SecurityConfig;
  /** Field identity metadata assigned by defineFields */
  key?: string;
  /** Field naming conventions */
  name?: NameCases;
  /** Type name alias (PascalCase) */
  type_name?: string;
  /** Constant name alias (UPPER_CASE) */
  constant_name?: string;
}

import type { StringFieldConfig } from './string';
import type { BooleanFieldConfig } from './boolean';
import type { EnumFieldConfig } from './enum';
import type { UuidFieldConfig } from './uuid';
import type { ForeignFieldConfig } from './foreign';
import { NameCases } from '../helpers';

export type FieldConfig = StringFieldConfig | BooleanFieldConfig | EnumFieldConfig<string> | UuidFieldConfig | ForeignFieldConfig;
