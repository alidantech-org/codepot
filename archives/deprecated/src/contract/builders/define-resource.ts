// src/contract/builders/define-resource.ts

import type { PropertiesAuthoringState } from '@/contract/types/authoring/4.properties-builder';
import type { SchemasAuthoringState } from '@/contract/types/authoring/5.schemas-builder';
import type { DefineResourceOptions, ResourceAuthoringState, ResourceBuilder } from '@/contract/types/authoring/6.resource-builder';
import type { RoutesAuthoringState, RoutePathAuthoringDefinition } from '@/contract/types/authoring/7.routes-builder';
import type { ErrorsAuthoringState, ErrorInputMap, ErrorsResult } from '@/contract/types/authoring/8.errors-builder';

import { resourceRef } from '@/contract/helpers/refs/authoring-ref-builder';

import { defineErrors } from './define-errors';
import { defineProperties } from './define-properties';
import { defineRoutes } from './define-routes';
import { defineSchemas } from './define-schemas';

// ============================================================================
// MERGE HELPERS
// ============================================================================

function mergeErrors(target: Partial<ErrorsAuthoringState>, source: Partial<ErrorsAuthoringState>): void {
  Object.assign(target, source);
}

// ============================================================================
// DEFINE RESOURCE
// ============================================================================

export function defineResource(options: DefineResourceOptions): ResourceBuilder {
  const properties: Partial<PropertiesAuthoringState> = {};
  const schemas: Partial<SchemasAuthoringState> = {};
  const errors: Partial<ErrorsAuthoringState> = {};
  const routes: RoutesAuthoringState = {};

  let defaultSecurity = options.security;

  function snapshot(): ResourceAuthoringState {
    return {
      key: options.key,
      folders: options.folders ?? [],
      defaults: {
        ...(options.defaults ?? {}),
        ...(defaultSecurity ? { security: defaultSecurity } : {}),
      },
      properties,
      schemas,
      errors,
      routes,
      description: options.description,
      deprecated: options.deprecated,
      meta: options.meta,
    };
  }

  const builder: ResourceBuilder = {
    get state() {
      return snapshot();
    },

    ref: resourceRef(options.key),

    defineProperties() {
      return defineProperties({
        scope: 'resource',
        resourceKey: options.key,
        state: properties,
      });
    },

    defineSchemas() {
      return defineSchemas({
        scope: 'resource',
        resourceKey: options.key,
        state: schemas,
      });
    },

    defineErrors<TInput extends ErrorInputMap>(input: TInput): ErrorsResult<TInput> {
      return defineErrors({
        state: errors,
      }).define(input);
    },

    defineRoutes() {
      return defineRoutes({
        resourceKey: options.key,
        routes,
      });
    },

    setSecurity(security) {
      defaultSecurity = security;
      return builder;
    },

    addErrors(nextErrors: ErrorsAuthoringState) {
      mergeErrors(errors, nextErrors);
      return builder;
    },

    addRoute(key: string, route: RoutePathAuthoringDefinition) {
      routes[key] = route;
      return builder;
    },

    snapshot,
  };

  return builder;
}
