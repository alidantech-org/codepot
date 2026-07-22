import type { ZodSourceRegistry } from '../zod/zod-source-registry.js';
import type { CodegenUiMeta } from '../codegen/codegen-extension.types.js';
import type { AccessRef } from '../access/access.types.js';
import type { NormalizedInfo } from '../info/info.types.js';

export interface ResourceContext {
  /**
   * Human-readable resource name.
   * Example: "User", "Vehicle Brand"
   */
  readonly name: string;

  /**
   * Actual HTTP URL path.
   * Example: "/users", "/auth/sessions"
   */
  readonly route: string;

  /**
   * OpenAPI tag.
   * Defaults to resource name.
   */
  readonly tag: string;

  /**
   * Generator metadata tags inherited by operations.
   */
  readonly tags: readonly string[];

  /**
   * Generated output grouping folders.
   * This is NOT a URL path.
   *
   * Example:
   * ["platform", "auth"]
   * ["references", "vehicles"]
   */
  readonly folders: readonly string[];

  /**
   * Generated resource alias.
   * Defaults to key.
   */
  readonly alias: string;

  /**
   * Resource-level UI generation intent.
   */
  readonly ui?: CodegenUiMeta;

  /**
   * Resource-level access policy inherited by routes.
   */
  readonly access?: AccessRef;

  readonly info?: NormalizedInfo;
}

export interface OptionalResourceContext {
  readonly resource?: ResourceContext;
  readonly zodRegistry?: ZodSourceRegistry;
}
