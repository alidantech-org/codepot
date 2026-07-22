// src/contract/types/ir/schema/definition.ts

import type { DtoDefinition } from './dto/definition';
import type { EntityDefinition } from './entity/definition';
import type { EntityFieldDefinition } from './entity/field/definition';
import type { ModelDefinition } from './model/definition';
import type { ParamsDefinition } from './params/definition';
import type { FieldSetDefinition } from './field-set/definition';

// ============================================================================
// SCHEMAS
// ============================================================================

export interface SchemasDefinition {
  entities: Record<string, EntityDefinition>;
  field_sets: Record<string, FieldSetDefinition>;
  models: Record<string, ModelDefinition>;
  dtos: Record<string, DtoDefinition>;
  params: Record<string, ParamsDefinition>;
}

export type RefSchema = EntityDefinition | EntityFieldDefinition | FieldSetDefinition | ModelDefinition | DtoDefinition;
