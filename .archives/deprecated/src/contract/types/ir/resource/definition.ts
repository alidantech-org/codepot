// src/contract/types/ir/resource/definition.ts

import type { DefinitionItem } from '../definition';
import type { Ref } from '../ref';
import type { SecurityPolicyDefinition } from '../security/definition';
import type { OperationDefinition } from './operation/definition';
import type { RoutesDefinition } from './route/definition';

// ============================================================================
// RESOURCE DEFAULTS
// ============================================================================

export interface ResourceDefaultsDefinition extends DefinitionItem {
  security?: Ref<SecurityPolicyDefinition>;
}

// ============================================================================
// RESOURCE
// ============================================================================

export interface ResourceDefinition extends DefinitionItem {
  /**
   * Compiled URL base path.
   * Example: /users, /posts, /admin/users
   */
  base_path: string;

  /**
   * Codegen/project organization folders.
   * These are not URL path segments.
   */
  folders: string[];

  defaults: ResourceDefaultsDefinition;

  operations: Record<string, OperationDefinition>;

  routes: RoutesDefinition;
}
