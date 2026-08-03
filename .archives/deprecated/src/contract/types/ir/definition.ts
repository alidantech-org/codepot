// src/contract/types/ir/definition.ts

// ============================================================================
// ROOT
// ============================================================================

import type { ContentTypeDefinition } from './content/definition';
import type { InfoDefinition } from './info/definition';
import type { PropertiesDefinition } from './properties/definition';
import type { ResourceDefinition } from './resource/definition';
import type { ResponsesDefinition } from './response/definition';
import type { SchemasDefinition } from './schema/definition';
import type { SecurityDefinition } from './security/definition';
import type { UrlDefinition } from './url/definition';
import type { Ref } from './ref';

// ============================================================================
// SHARED DEFINITION ITEM
// ============================================================================

export interface DefinitionItem {
  readonly meta?: Record<string, unknown>;
  readonly description?: string;
  readonly deprecated?: boolean;

  /**
   * Single validated source/owner link for promoted or source-linked IR items.
   *
   * The registry key carries searchable ownership:
   * identity.owner_key.original_key
   *
   * This ref carries validated ownership:
   * - #/resources/users
   * - #/schemas/entities/user
   * - #/properties/composites/inline_money
   */
  readonly ownership?: Ref;
}

// ============================================================================
// COMPILED CODEPOT DEFINITION
// ============================================================================

/**
 * Compiled Codepot IR/spec.
 *
 * This is the stable compiler output and the only contract shape codegen
 * should consume. Authoring-layer refs/helpers must not leak into this type.
 */
export interface CodepotDefinition extends DefinitionItem {
  /**
   * Codepot compiled IR/schema version.
   */
  codepot: string;

  /**
   * Stable API/project key.
   * Compiler should normalize this to snake_case.
   */
  key: string;

  /**
   * API major version.
   */
  version: number;

  info: InfoDefinition;

  urls: UrlDefinition[];

  /**
   * Reusable content type registry.
   */
  content_types: Record<string, ContentTypeDefinition>;

  /**
   * Reusable low-level properties.
   */
  properties: PropertiesDefinition;

  /**
   * Reusable schemas.
   */
  schemas: SchemasDefinition;

  /**
   * Reusable response registry.
   */
  responses: ResponsesDefinition;

  /**
   * API security registry.
   */
  security: SecurityDefinition;

  /**
   * API resources.
   */
  resources: Record<string, ResourceDefinition>;
}
