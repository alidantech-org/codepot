// src/contract/types/ir/schema/dto/definition.ts

import type { DefinitionItem } from '../../definition';
import type { Ref } from '../../ref';
import type { EntityFieldDefinition } from '../entity/field/definition';
import type { ModelDefinition } from '../model/definition';

// ============================================================================
// DTO FIELD
// ============================================================================

export interface DtoArrayFieldDefinition extends DefinitionItem {
  type: 'array';
  items: Ref<EntityFieldDefinition> | Ref<ModelDefinition> | Ref<DtoDefinition>;
  required?: boolean;
  nullable?: boolean;
}

export interface DtoRefFieldDefinition extends DefinitionItem {
  ref: Ref<EntityFieldDefinition> | Ref<ModelDefinition> | Ref<DtoDefinition>;
  required?: boolean;
  nullable?: boolean;
}

export type DtoFieldDefinition =
  | Ref<EntityFieldDefinition>
  | Ref<ModelDefinition>
  | Ref<DtoDefinition>
  | DtoRefFieldDefinition
  | DtoArrayFieldDefinition;

// ============================================================================
// DTO DEFINITION
// ============================================================================

export interface DtoDefinition extends DefinitionItem {
  /**
   * Direct DTO source.
   * Example: UserPublic DTO can be from UserPublic model.
   */
  from?: Ref<ModelDefinition> | Ref<DtoDefinition>;

  /**
   * DTO inheritance.
   * Example: UserResponse extends ApiResponse.
   */
  extends?: Ref<DtoDefinition>;

  /**
   * Compiled DTO fields only.
   * Inherited DTO fields should live on `extends`, not be duplicated here.
   */
  fields: Record<string, DtoFieldDefinition>;

  partial?: boolean;
}
