// src/contract/builders/define-version-contract.ts

import type {
  DefineVersionContractOptions,
  VersionAuthoringState,
  VersionBuilder,
  InfoDefinition,
  UrlDefinition,
} from '@/contract/types/authoring/2.version-builder';

import type { DefineResourceOptions, ResourceBuilder, ResourceAuthoringState } from '@/contract/types/authoring/6.resource-builder';

import type { ErrorInputMap, ErrorsResult, ErrorsAuthoringState } from '@/contract/types/authoring/8.errors-builder';

import type { PropertiesAuthoringState } from '@/contract/types/authoring/4.properties-builder';
import type { SchemasAuthoringState } from '@/contract/types/authoring/5.schemas-builder';
import type { SecurityAuthoringState } from '@/contract/types/authoring/9.security-builder';

import { defineErrors } from './define-errors';
import { defineProperties } from './define-properties';
import { defineResource } from './define-resource';
import { defineSchemas } from './define-schemas';
import { defineSecurity } from './define-security';

// ============================================================================
// DEFAULTS
// ============================================================================

const DEFAULT_CODEPOT_VERSION = '1.0';

// ============================================================================
// STATE FACTORIES
// ============================================================================

function createPropertiesState(initial?: Partial<PropertiesAuthoringState>): Partial<PropertiesAuthoringState> {
  return {
    primitives: initial?.primitives ?? {},
    enums: initial?.enums ?? {},
    composites: initial?.composites ?? {},
  };
}

function createSchemasState(initial?: Partial<SchemasAuthoringState>): Partial<SchemasAuthoringState> {
  return {
    entities: initial?.entities ?? {},
    models: initial?.models ?? {},
    dtos: initial?.dtos ?? {},
    params: initial?.params ?? {},
  };
}

function createErrorsState(initial?: Partial<ErrorsAuthoringState>): Partial<ErrorsAuthoringState> {
  return {
    ...(initial ?? {}),
  };
}

function createSecurityState(initial?: Partial<SecurityAuthoringState>): Partial<SecurityAuthoringState> {
  return {
    credentials: initial?.credentials ?? {},
    principals: initial?.principals ?? {},
    policies: initial?.policies ?? {},
  };
}

// ============================================================================
// MERGE HELPERS
// ============================================================================

function mergeProperties(target: Partial<PropertiesAuthoringState>, source: Partial<PropertiesAuthoringState>): void {
  Object.assign((target.primitives ??= {}), source.primitives ?? {});
  Object.assign((target.enums ??= {}), source.enums ?? {});
  Object.assign((target.composites ??= {}), source.composites ?? {});
}

function mergeSchemas(target: Partial<SchemasAuthoringState>, source: Partial<SchemasAuthoringState>): void {
  Object.assign((target.entities ??= {}), source.entities ?? {});
  Object.assign((target.models ??= {}), source.models ?? {});
  Object.assign((target.dtos ??= {}), source.dtos ?? {});
  Object.assign((target.params ??= {}), source.params ?? {});
}

function mergeErrors(target: Partial<ErrorsAuthoringState>, source: Partial<ErrorsAuthoringState>): void {
  Object.assign(target, source);
}

function mergeSecurity(target: Partial<SecurityAuthoringState>, source: Partial<SecurityAuthoringState>): void {
  target.credentials ??= {};
  target.principals ??= {};
  target.policies ??= {};

  Object.assign(target.credentials, source.credentials ?? {});
  Object.assign(target.principals, source.principals ?? {});
  Object.assign(target.policies, source.policies ?? {});
}

function snapshotResources(
  resources: Record<string, ResourceAuthoringState>,
  resourceBuilders: Record<string, ResourceBuilder>,
): Record<string, ResourceAuthoringState> {
  return {
    ...resources,
    ...Object.fromEntries(
      Object.entries(resourceBuilders).map(([key, builder]) => [key, builder.snapshot() as unknown as ResourceAuthoringState]),
    ),
  };
}

// ============================================================================
// DEFINE VERSION CONTRACT
// ============================================================================

export function defineVersionContract(options: DefineVersionContractOptions): VersionBuilder {
  const properties = createPropertiesState(options.properties);
  const schemas = createSchemasState(options.schemas);
  const errors = createErrorsState(options.errors);
  const security = createSecurityState(options.security);

  const resources: Record<string, ResourceAuthoringState> = {
    ...(options.resources ?? {}),
  };

  const resourceBuilders: Record<string, ResourceBuilder> = {};

  function snapshot(): VersionAuthoringState {
    return {
      codepot: options.codepot ?? DEFAULT_CODEPOT_VERSION,
      key: options.key,
      version: options.version,
      info: options.info,
      urls: options.urls ?? [],

      properties,
      schemas,
      errors,
      security,
      resources: snapshotResources(resources, resourceBuilders),

      description: options.description,
      deprecated: options.deprecated,
      meta: options.meta,
    };
  }

  const builder: VersionBuilder = {
    get state() {
      return snapshot();
    },

    defineProperties() {
      return defineProperties({
        scope: 'version',
        state: properties,
      });
    },

    defineSchemas() {
      return defineSchemas({
        scope: 'version',
        state: schemas,
      });
    },

    defineErrors<TInput extends ErrorInputMap>(input: TInput): ErrorsResult<TInput> {
      return defineErrors({
        state: errors,
      }).define(input);
    },

    defineSecurity() {
      return defineSecurity({
        state: security,
      });
    },

    defineResource(resourceOptions: DefineResourceOptions) {
      const resourceBuilder = defineResource(resourceOptions);

      resourceBuilders[resourceOptions.key] = resourceBuilder;

      return resourceBuilder;
    },

    addResource(key, resource) {
      resources[key] = resource;
      return builder;
    },

    addProperties(nextProperties) {
      mergeProperties(properties, nextProperties);
      return builder;
    },

    addSchemas(nextSchemas) {
      mergeSchemas(schemas, nextSchemas);
      return builder;
    },

    addErrors(nextErrors) {
      mergeErrors(errors, nextErrors);
      return builder;
    },

    addSecurity(nextSecurity) {
      mergeSecurity(security, nextSecurity);
      return builder;
    },

    snapshot,
  };

  return builder;
}
