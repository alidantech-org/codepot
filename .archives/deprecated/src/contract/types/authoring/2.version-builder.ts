import type { DefinitionItem, PropertiesAuthoringState, PropertiesBuilder } from './4.properties-builder';
import type { SchemasAuthoringState, SchemasBuilder } from './5.schemas-builder';
import type { DefineResourceOptions, ResourceBuilder, ResourceAuthoringState } from './6.resource-builder';
import type { ErrorInputMap, ErrorsResult, ErrorsAuthoringState } from './8.errors-builder';
import type { SecurityAuthoringState, SecurityBuilder } from './9.security-builder';

// ============================================================================
// AUTHORING URL/INFO TYPES
// ============================================================================

export interface UrlDefinition extends DefinitionItem {
  readonly key: string;
  readonly kind: string;
  readonly env: string;
  readonly uri: string;
}

export interface InfoDefinition extends DefinitionItem {
  readonly title: string;
  readonly version: string;
  readonly summary?: string;
}

export interface DefineVersionContractOptions {
  /**
   * Codepot IR/schema version.
   * Example: "1.0"
   */
  readonly codepot?: string;

  /**
   * Stable API/project key.
   * Example: "riderescue_api"
   */
  readonly key: string;

  /**
   * API major version.
   * Example: 1
   */
  readonly version: number;

  readonly info: InfoDefinition;

  readonly urls?: readonly UrlDefinition[];

  /**
   * Optional prebuilt authoring sections.
   * Useful while some authoring helpers are not implemented yet.
   */
  readonly properties?: Partial<PropertiesAuthoringState>;
  readonly schemas?: Partial<SchemasAuthoringState>;
  readonly errors?: Partial<ErrorsAuthoringState>;
  readonly security?: Partial<SecurityAuthoringState>;
  readonly resources?: Record<string, ResourceAuthoringState>;

  readonly meta?: Record<string, unknown>;
  readonly description?: string;
  readonly deprecated?: boolean;
}

export interface VersionAuthoringState {
  readonly codepot: string;
  readonly key: string;
  readonly version: number;
  readonly info: InfoDefinition;
  readonly urls: readonly UrlDefinition[];

  readonly properties: Partial<PropertiesAuthoringState>;
  readonly schemas: Partial<SchemasAuthoringState>;
  readonly errors: Partial<ErrorsAuthoringState>;
  readonly security: Partial<SecurityAuthoringState>;
  readonly resources: Record<string, ResourceAuthoringState>;

  readonly meta?: Record<string, unknown>;
  readonly description?: string;
  readonly deprecated?: boolean;
}

export interface VersionBuilder {
  /**
   * Current authoring state.
   * Compiler later normalizes this into final Codepot IR.
   */
  readonly state: VersionAuthoringState;

  /**
   * Version-level reusable property sources:
   * primitives, enums, composites, and reusable refs.
   */
  defineProperties(): PropertiesBuilder;

  /**
   * Version-level schemas:
   * entities, DTOs, params, model overrides, field-set overrides.
   */
  defineSchemas(): SchemasBuilder;

  /**
   * Version-level reusable API errors.
   */
  defineErrors<TInput extends ErrorInputMap>(input: TInput): ErrorsResult<TInput>;

  /**
   * Version-level security intent metadata:
   * credentials, principals, and policies.
   */
  defineSecurity(): SecurityBuilder;

  /**
   * Resource authoring entry.
   */
  defineResource(options: DefineResourceOptions): ResourceBuilder;

  /**
   * Allows adding a prebuilt resource while helpers are incomplete.
   */
  addResource(key: string, resource: ResourceAuthoringState): VersionBuilder;

  /**
   * Allows adding/preloading properties while helpers are incomplete.
   */
  addProperties(properties: Partial<PropertiesAuthoringState>): VersionBuilder;

  /**
   * Allows adding/preloading schemas while helpers are incomplete.
   */
  addSchemas(schemas: Partial<SchemasAuthoringState>): VersionBuilder;

  /**
   * Allows adding/preloading reusable errors while helpers are incomplete.
   */
  addErrors(errors: Partial<ErrorsAuthoringState>): VersionBuilder;

  /**
   * Allows adding/preloading security while helpers are incomplete.
   */
  addSecurity(security: Partial<SecurityAuthoringState>): VersionBuilder;

  /**
   * Authoring snapshot.
   * This is still authoring state, not final compiled Codepot IR.
   */
  snapshot(): VersionAuthoringState;
}
