import { createAccessBuilder, defineAccess } from '../access/access';
import { createSchemaComponentRegistry, defineParameters, defineRequestBodies, defineResponses, defineSchemas } from '../components/components';
import type { ParameterComponentInput, RequestBodyComponentInput, ResponseComponentInput, SchemaComponentValue } from '../components/component.types';
import { createAuthoringState, normalizeInfo } from '../core/normalize';
import { defineEntities, defineEntityRelations } from '../entities/entities';
import type { ConcreteEntityDefinitionInput, EntityDefinitionFactory, EntityRelationsInput } from '../entities/entity.types';
import { defineHooks } from '../hooks/hooks';
import type { RuntimeHookDefinition } from '../hooks/hooks.types';
import { defineProperties } from '../properties/define-properties';
import type { PropertyGroupOptions, ZodPropertyDefinitionFieldMap } from '../properties/property.types';
import { defineRoutes } from '../routes/routes';
import type { DefineRoutesInput, RouteRegistry, RoutesDefinitionBuilder } from '../routes/route.types';
import type { AccessDefinitionInput } from '../access/access.types';
import type { DefineResourceOptions, ResourceBuilder } from './resource.types';
import type { InfoInput } from '../core/authoring.types';

export function defineResource(options: DefineResourceOptions): ResourceBuilder {
  const state = createAuthoringState();
  const normalizedInfo = options.info ? normalizeInfo(options.info) : undefined;
  const context: import('../core/authoring.types').ResourceContext = {
    name: options.name,
    route: options.route,
    tag: options.tag ?? options.name,
    tags: [...(options.tags ?? [])],
    folders: (options.folders ?? []).map((item) => item.trim()).filter(Boolean),
    alias: options.alias ?? options.name,
    ...(options.ui ? { ui: typeof options.ui === 'string' ? { role: options.ui } : options.ui } : {}),
    ...(options.access ? { access: options.access } : {}),
    ...(normalizedInfo ? { info: normalizedInfo } : {}),
  };
  const properties: ResourceBuilder['properties'] = [];
  const schemas = createSchemaComponentRegistry(context.name);
  const schemaComponents: ResourceBuilder['schemaComponents'] = [schemas];
  const parameterComponents: ResourceBuilder['parameterComponents'] = [];
  const requestBodyComponents: ResourceBuilder['requestBodyComponents'] = [];
  const responseComponents: ResourceBuilder['responseComponents'] = [];
  const accessComponents: ResourceBuilder['accessComponents'] = [];
  const hookComponents: ResourceBuilder['hookComponents'] = [];
  const entityComponents: ResourceBuilder['entityComponents'] = [];
  const entityRelationComponents: ResourceBuilder['entityRelationComponents'] = [];
  const routeRegistries: ResourceBuilder['routeRegistries'] = [];
  const routes = { ref: {} as Record<string, import('../refs/ref.types').RouteRef> };
  const access = createAccessBuilder();

  function defineResourceRoutes(): RoutesDefinitionBuilder;
  function defineResourceRoutes(input: DefineRoutesInput, name?: string): RouteRegistry;
  function defineResourceRoutes(input?: DefineRoutesInput, name?: string): RouteRegistry | RoutesDefinitionBuilder {
    const routeOptions = { name: name ?? context.name, resource: context };
    if (input) {
      const registry = defineRoutes(routeOptions, input) as RouteRegistry;
      routeRegistries.push(registry);
      Object.assign(routes.ref, registry.ref);
      return registry;
    }
    const routeBuilder = defineRoutes(routeOptions) as RoutesDefinitionBuilder;
    const wrapper: RoutesDefinitionBuilder = {
      params(parameters): RoutesDefinitionBuilder { routeBuilder.params(parameters); return wrapper; },
      routes(routeInput): RouteRegistry {
        const registry = routeBuilder.routes(routeInput);
        routeRegistries.push(registry);
        Object.assign(routes.ref, registry.ref);
        return registry;
      },
    };
    return wrapper;
  }

  const builder: ResourceBuilder = {
    context, state, properties, schemas, schemaComponents, parameterComponents, requestBodyComponents,
    responseComponents, accessComponents, hookComponents, entityComponents, entityRelationComponents,
    routeRegistries, routes, access,
    defineProperties<TName extends string, TFields extends ZodPropertyDefinitionFieldMap>(name: TName, fields: TFields, groupOptions?: PropertyGroupOptions) {
      const registry = defineProperties({ name: context.name, resource: context }, name, fields, groupOptions);
      properties.push({ name: registry.name, definitions: [...registry.definitions], ref: { [name]: registry.ref } });
      return registry;
    },
    defineSchemas<const TInput extends Record<string, SchemaComponentValue>>(input: TInput, name?: string) {
      return defineSchemas({ name: name ?? context.name, resource: context, state }, input, schemas);
    },
    defineParameters<const TInput extends Record<string, ParameterComponentInput>>(input: TInput, name?: string) {
      const registry = defineParameters({ name: name ?? context.name, resource: context, state }, input); parameterComponents.push(registry); return registry;
    },
    defineRequestBodies<const TInput extends Record<string, RequestBodyComponentInput>>(input: TInput, name?: string) {
      const registry = defineRequestBodies({ name: name ?? context.name, resource: context, state }, input); requestBodyComponents.push(registry); return registry;
    },
    defineResponses<const TInput extends Record<string, ResponseComponentInput>>(input: TInput, name?: string) {
      const registry = defineResponses({ name: name ?? context.name, resource: context, state }, input); responseComponents.push(registry); return registry;
    },
    defineAccess<const TInput extends Record<string, AccessDefinitionInput>>(input: TInput) {
      const registry = defineAccess(input, { resource: context }); accessComponents.push(registry); return registry;
    },
    defineHooks<const TInput extends Record<string, RuntimeHookDefinition>>(input: TInput) {
      const registry = defineHooks(input, { resource: context }); hookComponents.push(registry); return registry;
    },
    defineEntities<const TInput extends Record<string, ConcreteEntityDefinitionInput>>(input: TInput | EntityDefinitionFactory<TInput>) {
      const registry = defineEntities({ name: context.name, resource: context }, input); entityComponents.push(registry); return registry;
    },
    defineEntityRelations(input: EntityRelationsInput) {
      const registry = defineEntityRelations({ resource: context }, input); entityRelationComponents.push(registry); return registry;
    },
    defineRoutes: defineResourceRoutes,
    info(info: InfoInput): ResourceBuilder {
      const current = context.info;
      const next = normalizeInfo(info);
      Object.assign(context, { info: { ...(current ?? {}), ...(next ?? {}) } });
      return builder;
    },
  };
  return builder;
}
