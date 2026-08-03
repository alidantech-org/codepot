// src/contract/types/ir/resource/operation/definition.ts

import type { DefinitionItem } from '../../definition';
import type { Ref } from '../../ref';
import type { DtoDefinition } from '../../schema/dto/definition';
import type { ModelDefinition } from '../../schema/model/definition';
import type { ParamsDefinition } from '../../schema/params/definition';
import type { SecurityPrincipalDefinition } from '../../security/definition';
import type { ErrorResponseDefinition } from '../../response/errors/definition';

// ============================================================================
// OPERATION SCHEMA REFS
// ============================================================================

export type OperationSchemaRef = Ref<DtoDefinition> | Ref<ModelDefinition>;

export type OperationContextRef = Ref<DtoDefinition> | Ref<ModelDefinition> | Ref<SecurityPrincipalDefinition>;

// ============================================================================
// INPUT / OUTPUT
// ============================================================================

export interface OperationInputDefinition extends DefinitionItem {
  /**
   * Injected request contexts such as auth user, tenant, locale, etc.
   */
  context?: OperationContextRef[];

  /**
   * Path parameter schema.
   */
  params?: Ref<ParamsDefinition>;

  /**
   * Query string schema.
   */
  query?: OperationSchemaRef;

  /**
   * Request body schema.
   */
  body?: OperationSchemaRef;
}

export interface OperationOutputDefinition extends DefinitionItem {
  /**
   * Success payload schema.
   */
  result?: OperationSchemaRef;

  /**
   * Typed error responses.
   */
  errors?: Ref<ErrorResponseDefinition>[];
}

// ============================================================================
// OPERATION
// ============================================================================

export interface OperationDefinition extends DefinitionItem {
  input: OperationInputDefinition;
  output: OperationOutputDefinition;
}
