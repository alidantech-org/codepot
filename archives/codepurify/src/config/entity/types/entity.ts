// ─── codepurify/fields/entity.ts ─────────────────────────────────────────────────

import { FieldConfig } from './base';
import { CheckConfig } from './check';
import { RelationConfigUnion } from './relation';
import { TransitionConfig } from './transition';
import { WorkflowConfig } from './workflow';
import { IndexConfig } from './indexes';
import { CodepurifyTemplatesFile } from '@/config/global';

// ─── Entity options ───────────────────────────────────────────────────────────

export interface EntityOptions {
  timestamps?: boolean;
  audit?: boolean;
  softDelete?: boolean;
}

// ─── Entity config interface ─────────────────────────────────────────────────────

/**
 * Configuration interface for defining entity structures and behaviors
 */
export interface IEntityConfig {
  /**
   * Base entity constructor for inheritance patterns
   * @type {EntityConfigConstructor | null}
   */
  base: EntityConfigConstructor | null;

  /**
   * Unique identifier for the entity type
   * @type {string}
   */
  key: string;

  /**
   * Logical grouping for related entities
   * @type {string}
   */
  group_key: string;

  /**
   * Field definitions with their types and configurations
   * @type {Record<string, FieldConfig>}
   */
  fields: Record<string, FieldConfig>;

  /**
   * Relationship definitions to other entities
   * @type {Record<string, RelationConfigUnion>}
   */
  relations: Record<string, RelationConfigUnion>;

  /**
   * Database index definitions for performance optimization
   * @type {readonly IndexConfig[|}
   */
  indexes: readonly IndexConfig[];

  /**
   * Data validation and constraint rules
   * @type {readonly CheckConfig[|}
   */
  checks: readonly CheckConfig[];

  /**
   * Entity-level options like timestamps and auditing
   * @type {EntityOptions}
   */
  options: EntityOptions;

  /**
   * Code generation templates to be applied
   * @type {readonly string[|}
   */
  templates: readonly CodepurifyTemplatesFile[];

  /**
   * State transition definitions for entity lifecycle
   * @type {readonly TransitionConfig[|}
   */
  transitions: readonly TransitionConfig[];

  /**
   * Workflow definitions for complex business processes
   * @type {readonly WorkflowConfig[|}
   */
  workflows: readonly WorkflowConfig[];
}

// ─── Type constraint ─────────────────────────────────────────────────────────

export type EntityConfigConstructor = abstract new (...args: any[]) => IEntityConfig;
