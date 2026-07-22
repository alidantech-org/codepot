import type { ResourceAuthoringRef } from './3.authoring-ref';
import type { DefinitionItem, PropertiesAuthoringState, PropertiesBuilder } from './4.properties-builder';
import type { SchemasAuthoringState, SchemasBuilder } from './5.schemas-builder';
import type { ErrorInputMap, ErrorsResult, ErrorsAuthoringState } from './8.errors-builder';
import type { RoutesAuthoringState, RoutesBuilder, RoutePathAuthoringDefinition } from './7.routes-builder';
import type { RouteSecurityInput } from './9.security-builder';

// ============================================================================
// RESOURCE DEFAULTS
// ============================================================================

export interface ResourceDefaults {
  readonly security?: RouteSecurityInput;
}

// ============================================================================
// DEFINE RESOURCE OPTIONS
// ============================================================================

export interface DefineResourceOptions extends DefinitionItem {
  /**
   * Stable resource key.
   * Example: "users", "vehicle_brands", "auth_sessions"
   */
  readonly key: string;

  /**
   * Generated/code organization folders.
   * This is not a URL path.
   *
   * Example:
   * ["platform", "auth"]
   */
  readonly folders?: readonly string[];

  /**
   * Resource-level default security.
   * Applied to routes unless route-level security overrides it.
   */
  readonly security?: RouteSecurityInput;

  /**
   * Other resource-level default behavior.
   */
  readonly defaults?: Partial<ResourceDefaults>;
}

// ============================================================================
// RESOURCE AUTHORING STATE
// ============================================================================

export interface ResourceAuthoringState extends DefinitionItem {
  readonly key: string;

  readonly folders: readonly string[];

  readonly defaults: ResourceDefaults;

  readonly properties: Partial<PropertiesAuthoringState>;

  /**
   * Resource-scoped schemas:
   * entities, DTOs, params, model overrides, field-set overrides.
   */
  readonly schemas: Partial<SchemasAuthoringState>;

  /**
   * Resource-scoped reusable API errors.
   */
  readonly errors: Partial<ErrorsAuthoringState>;

  readonly routes: RoutesAuthoringState;
}

// ============================================================================
// RESOURCE BUILDER
// ============================================================================

export interface ResourceBuilder {
  readonly state: ResourceAuthoringState;

  /**
   * Resource authoring ref.
   */
  readonly ref: ResourceAuthoringRef;

  /**
   * Resource-scoped reusable property sources:
   * primitives, enums, composites, and refs.
   */
  defineProperties(): PropertiesBuilder;

  /**
   * Resource-scoped schemas:
   * entities, DTOs, params, model overrides, field-set overrides.
   */
  defineSchemas(): SchemasBuilder;

  /**
   * Resource-scoped reusable API errors.
   */
  defineErrors<TInput extends ErrorInputMap>(input: TInput): ErrorsResult<TInput>;

  /**
   * Resource-scoped routes and operations.
   */
  defineRoutes(): RoutesBuilder;

  /**
   * Set/replace resource-level default security.
   */
  setSecurity(security: RouteSecurityInput): ResourceBuilder;

  /**
   * Adds/preloads resource-scoped reusable errors while helpers are incomplete.
   */
  addErrors(errors: Partial<ErrorsAuthoringState>): ResourceBuilder;

  /**
   * Adds/preloads route data while route helpers are incomplete.
   */
  addRoute(key: string, route: RoutePathAuthoringDefinition): ResourceBuilder;

  /**
   * Resource authoring snapshot.
   * Compiler later normalizes this into ResourceDefinition.
   */
  snapshot(): ResourceAuthoringState;
}
