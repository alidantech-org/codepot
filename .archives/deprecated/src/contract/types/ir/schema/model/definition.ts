// src/contract/types/ir/schema/model/definition.ts

import type { DefinitionItem } from '../../definition';
import type { Ref } from '../../ref';
import type { EntityDefinition } from '../entity/definition';
import type { EntityFieldDefinition } from '../entity/field/definition';
import type { FieldSetDefinition } from '../field-set/definition';

// ============================================================================
// MODEL FIELD
// ============================================================================

export interface ModelArrayFieldDefinition extends DefinitionItem {
  type: 'array';
  items: Ref<EntityFieldDefinition> | Ref<ModelDefinition>;
  required?: boolean;
  nullable?: boolean;
}

export type ModelFieldDefinition = Ref<EntityFieldDefinition> | ModelArrayFieldDefinition;

// ============================================================================
// MODEL DEFINITION
// ============================================================================

export interface ModelDefinition extends DefinitionItem {
  from: Ref<EntityDefinition>;

  /**
   * Preserve inheritance when the source entity extends another entity and the
   * parent has the same compiled model variant.
   */
  extends?: Ref<ModelDefinition>;

  partial?: boolean;

  /**
   * Optional model-linked field sets.
   *
   * These are refs to root `schemas.field_sets` entries. Model `fields` remains
   * the direct field map; these refs are helper metadata for codegen and query UI.
   */
  field_sets?: {
    readonly select?: Ref<FieldSetDefinition>;
    readonly sort?: Ref<FieldSetDefinition>;
    readonly filter?: Ref<FieldSetDefinition>;
    readonly create?: Ref<FieldSetDefinition>;
    readonly update?: Ref<FieldSetDefinition>;
    readonly relations?: Ref<FieldSetDefinition>;
  };

  /**
   * Compiled model fields only.
   * Inherited model fields should live on `extends`, not be duplicated here.
   */
  fields: Record<string, ModelFieldDefinition>;
}
