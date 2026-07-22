// src/contract/types/ir/resource/route/definition.ts

import type { DefinitionItem } from '../../definition';
import type { Ref } from '../../ref';
import type { ContentTypeDefinition } from '../../content/definition';
import type { ErrorResponseDefinition } from '../../response/errors/definition';
import type { DtoDefinition } from '../../schema/dto/definition';
import type { ModelDefinition } from '../../schema/model/definition';
import type { ParamsDefinition } from '../../schema/params/definition';
import type { SecurityPolicyDefinition } from '../../security/definition';
import type { OperationDefinition } from '../operation/definition';

// ============================================================================
// HTTP METHOD
// ============================================================================

export const HttpMethod = {
  get: 'get',
  post: 'post',
  put: 'put',
  patch: 'patch',
  delete: 'delete',
  options: 'options',
  head: 'head',
} as const;

export type HttpMethod = (typeof HttpMethod)[keyof typeof HttpMethod];

// ============================================================================
// ROUTE SCHEMA / CONTENT
// ============================================================================

export type RouteSchemaRef = Ref<DtoDefinition> | Ref<ModelDefinition>;

export interface RouteBodyDefinition extends DefinitionItem {
  schema: RouteSchemaRef;
  content_type: Ref<ContentTypeDefinition>;
  content_types?: readonly Ref<ContentTypeDefinition>[];
}

export interface RouteOutputDefinition extends DefinitionItem {
  status: number;
  schema?: RouteSchemaRef;
  content_type?: Ref<ContentTypeDefinition>;
}

export interface RouteInlineResponseDefinition extends DefinitionItem {
  status?: number;
  schema?: RouteSchemaRef;
  content_type?: Ref<ContentTypeDefinition>;
  content_types?: readonly Ref<ContentTypeDefinition>[];
  headers?: Record<string, RouteSchemaRef>;
}

export type RouteResponseDefinition = Ref<ErrorResponseDefinition> | RouteInlineResponseDefinition;

// ============================================================================
// ROUTE METHOD
// ============================================================================

export interface RouteMethodDefinition extends DefinitionItem {
  operation: Ref<OperationDefinition>;

  security?: Ref<SecurityPolicyDefinition> | SecurityPolicyDefinition;

  params?: Ref<ParamsDefinition>;
  query?: RouteSchemaRef;
  body?: RouteBodyDefinition;

  /**
   * Response map keyed by HTTP status code.
   */
  responses: Record<number, RouteResponseDefinition>;
}

// ============================================================================
// ROUTES
// ============================================================================

export interface RoutePathDefinition extends DefinitionItem {
  /**
   * Full route path including the resource base path.
   *
   * Example:
   * /users/:id
   */
  readonly path: string;

  /**
   * Path-level parameters for this path.
   *
   * This avoids scanning every method to discover route params.
   */
  readonly parameters?: Record<string, Ref<ParamsDefinition>>;

  /**
   * HTTP methods available for this full path.
   */
  readonly methods: Partial<Record<HttpMethod, RouteMethodDefinition>>;
}

/**
 * Route map keyed by full absolute path.
 */
export type RoutesDefinition = Record<string, RoutePathDefinition>;
