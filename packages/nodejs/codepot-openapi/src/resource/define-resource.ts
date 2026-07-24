import { createSchemaComponentRegistry, defineSchemas } from '../components/schemas/define-schemas.js';
import type {
  SchemaComponentRegistry,
  SchemaComponentValue,
} from '../components/schemas/schema-component.types.js';

import { defineParameters } from '../components/parameters/define-parameters.js';
import type { ParameterComponentRegistry, ParameterComponentDefinition } from '../components/parameters/parameter-component.types.js';

import { defineRequestBodies } from '../components/request-bodies/define-request-bodies.js';
import type {
  RequestBodyComponentRegistry,
  RequestBodyComponentDefinition,
} from '../components/request-bodies/request-body-component.types.js';

import { defineResponses } from '../components/responses/define-responses.js';
import type { ResponseComponentRegistry, ResponseComponentDefinition } from '../components/responses/response-component.types.js';

import type { PropertyGroupOptions, PropertyRegistry, ZodPropertyDefinitionFieldMap } from '../properties/property.types.js';

import { defineRoutes } from '../routes/define-routes.js';
import type { DefineRoutesInputLike, RouteRegistry, RoutesDefinitionBuilder } from '../routes/route.types.js';

import type { ResourceContext } from './resource-context.types.js';
import { defineProperties } from '../properties/define-properties.js';
import { normalizeCodegenUiInput } from '../codegen/codegen-ui.js';
import type { CodegenUiInput } from '../codegen/codegen-extension.types.js';
import { defineAccess } from '../access/define-access.js';
import { createAccessBuilder, type AccessBuilder } from '../access/access-builder.js';
import type { AccessDefinitionInput, AccessRef, AccessRegistry } from '../access/access.types.js';
import { defineHooks } from '../hooks/define-hooks.js';
import type { RuntimeHookDefinition, RuntimeHookRegistry } from '../hooks/runtime-hooks.types.js';
import { defineEntities, defineEntityRelations } from '../entities/define-entities.js';
import type { EntityDefinitionFactory } from '../entities/define-entities.js';
import type {
  ConcreteEntityDefinitionInput,
  EntityRegistry,
  EntityRelationRegistry,
  EntityRelationsInput,
} from '../entities/entity.types.js';
import type { InfoInput } from '../info/info.types.js';
import { normalizeInfo } from '../info/normalize-info.js';

export interface DefineResourceOptions {
  /**
   * Human-readable resource name.
   * Example: "User", "Vehicle Brand"
   */
  name: string;

  /**
   * Actual HTTP URL path.
   * Example: "/users", "/auth/sessions"
   */
  route: string;

  /**
   * Optional OpenAPI tag.
   * Defaults to name.
   */
  tag?: string;

  /**
   * Generator metadata tags inherited by operations.
   */
  tags?: readonly string[];

  /**
   * Generated output grouping folders.
   * This is NOT a URL path.
   *
   * Example:
   * ["platform", "auth"]
   * ["references", "vehicles"]
   */
  folders?: readonly string[];

  /**
   * Optional generated resource alias.
   * Defaults to key.
   */
  alias?: string;

  /**
   * Resource-level UI generation intent.
   */
  ui?: CodegenUiInput;

  /**
   * Resource-level access policy inherited by operations.
   */
  access?: AccessRef;

  info?: InfoInput;
}

export interface ResourceBuilder {
  readonly context: ResourceContext;

  readonly properties: PropertyRegistry[];
  readonly schemas: SchemaComponentRegistry;
  readonly schemaComponents: SchemaComponentRegistry[];
  readonly parameterComponents: ParameterComponentRegistry[];
  readonly requestBodyComponents: RequestBodyComponentRegistry[];
  readonly responseComponents: ResponseComponentRegistry[];
  readonly accessComponents: AccessRegistry[];
  readonly hookComponents: RuntimeHookRegistry[];
  readonly entityComponents: EntityRegistry[];
  readonly entityRelationComponents: EntityRelationRegistry[];
  readonly routeRegistries: RouteRegistry[];
  readonly routes: {
    readonly ref: Record<string, import('../refs/ref.types.js').RouteRef>;
  };
  readonly access: AccessBuilder;

  defineProperties<TName extends string, TFields extends ZodPropertyDefinitionFieldMap>(
    name: TName,
    fields: TFields,
    options?: PropertyGroupOptions,
  ): ReturnType<typeof defineProperties<TName, TFields>>;

  defineSchemas<const TInput extends Record<string, SchemaComponentValue>>(
    input: TInput,
    name?: string,
  ): SchemaComponentRegistry<TInput>;

  defineParameters<TInput extends Record<string, Omit<ParameterComponentDefinition, 'key'>>>(
    input: TInput,
    name?: string,
  ): ReturnType<typeof defineParameters<TInput>>;

  defineRequestBodies<TInput extends Record<string, Omit<RequestBodyComponentDefinition, 'name'>>>(
    input: TInput,
    name?: string,
  ): ReturnType<typeof defineRequestBodies<TInput>>;

  defineResponses<TInput extends Record<string, Omit<ResponseComponentDefinition, 'name'>>>(
    input: TInput,
    name?: string,
  ): ReturnType<typeof defineResponses<TInput>>;

  defineAccess<const TInput extends Record<string, AccessDefinitionInput>>(input: TInput): AccessRegistry<TInput>;
  defineHooks<const TInput extends Record<string, RuntimeHookDefinition>>(input: TInput): RuntimeHookRegistry<TInput>;
  defineEntities<const TInput extends Record<string, ConcreteEntityDefinitionInput>>(
    input: TInput | EntityDefinitionFactory<TInput>,
  ): EntityRegistry<TInput>;
  defineEntityRelations(input: EntityRelationsInput): EntityRelationRegistry;

  defineRoutes(): RoutesDefinitionBuilder;
  defineRoutes(routes: DefineRoutesInputLike, name?: string): RouteRegistry;
  info(info: InfoInput): ResourceBuilder;
}

function normalizeFolders(folders?: readonly string[]): readonly string[] {
  return folders?.map((folder) => folder.trim()).filter(Boolean) ?? [];
}

export function defineResource(options: DefineResourceOptions): ResourceBuilder {
  const context: ResourceContext = {
    name: options.name,
    route: options.route,
    tag: options.tag ?? options.name,
    tags: options.tags ?? [],
    folders: normalizeFolders(options.folders),
    alias: options.alias ?? options.name,
    ui: normalizeCodegenUiInput(options.ui),
    access: options.access,
    info: normalizeInfo(options.info),
  };

  const properties: PropertyRegistry[] = [];
  const schemas = createSchemaComponentRegistry(context.name);
  const schemaComponents: SchemaComponentRegistry[] = [schemas];
  const parameterComponents: ParameterComponentRegistry[] = [];
  const requestBodyComponents: RequestBodyComponentRegistry[] = [];
  const responseComponents: ResponseComponentRegistry[] = [];
  const accessComponents: AccessRegistry[] = [];
  const hookComponents: RuntimeHookRegistry[] = [];
  const entityComponents: EntityRegistry[] = [];
  const entityRelationComponents: EntityRelationRegistry[] = [];
  const routeRegistries: RouteRegistry[] = [];
  const routes = { ref: {} as Record<string, import('../refs/ref.types.js').RouteRef> };
  const access = createAccessBuilder();

  function defineResourceProperties<TName extends string, TFields extends ZodPropertyDefinitionFieldMap>(
    name: TName,
    fields: TFields,
    groupOptions?: PropertyGroupOptions,
  ) {
    const registry = defineProperties({
      name: context.name,
      resource: context,
    }, name, fields, groupOptions);

    properties.push({
      name: registry.name,
      definitions: registry.definitions,
      ref: {
        [name]: registry.ref,
      },
    });
    return registry;
  }

  const defineResourceSchemas: ResourceBuilder['defineSchemas'] = <const TInput extends Record<string, SchemaComponentValue>>(
    input: TInput,
    name?: string,
  ): SchemaComponentRegistry<TInput> => {
    const registry = defineSchemas(
      {
        name: name ?? context.name,
        resource: context,
      },
      input,
      schemas,
    ) as SchemaComponentRegistry<TInput>;

    return registry;
  };

  function defineResourceParameters<TInput extends Record<string, Omit<ParameterComponentDefinition, 'key'>>>(
    input: TInput,
    name?: string,
  ) {
    const registry = defineParameters(
      {
        name: name ?? context.name,
        resource: context,
      },
      input,
    );

    parameterComponents.push(registry);
    return registry;
  }

  function defineResourceRequestBodies<TInput extends Record<string, Omit<RequestBodyComponentDefinition, 'name'>>>(
    input: TInput,
    name?: string,
  ) {
    const registry = defineRequestBodies(
      {
        name: name ?? context.name,
        resource: context,
      },
      input,
    );

    requestBodyComponents.push(registry);
    return registry;
  }

  function defineResourceResponses<TInput extends Record<string, Omit<ResponseComponentDefinition, 'name'>>>(input: TInput, name?: string) {
    const registry = defineResponses(
      {
        name: name ?? context.name,
        resource: context,
      },
      input,
    );

    responseComponents.push(registry);
    return registry;
  }

  function defineResourceAccess<const TInput extends Record<string, AccessDefinitionInput>>(input: TInput): AccessRegistry<TInput> {
    const registry = defineAccess(input, {
      owner: {
        resource: {
          name: context.alias,
          path: context.folders,
        },
      },
    });

    accessComponents.push(registry);
    return registry;
  }

  function defineResourceHooks<const TInput extends Record<string, RuntimeHookDefinition>>(input: TInput): RuntimeHookRegistry<TInput> {
    const registry = defineHooks(input, {
      owner: {
        resource: {
          name: context.alias,
          path: context.folders,
        },
      },
    });

    hookComponents.push(registry);
    return registry;
  }

  function defineResourceEntities<const TInput extends Record<string, ConcreteEntityDefinitionInput>>(
    input: TInput | EntityDefinitionFactory<TInput>,
  ): EntityRegistry<TInput> {
    const registry = defineEntities(
      {
        name: context.name,
        resource: context,
      },
      input,
    );

    entityComponents.push(registry);
    return registry;
  }

  function defineResourceEntityRelations(input: EntityRelationsInput): EntityRelationRegistry {
    const registry = defineEntityRelations(
      {
        resource: {
          name: context.alias,
          path: context.folders,
        },
      },
      input,
    );

    entityRelationComponents.push(registry);
    return registry;
  }

  function defineResourceRoutes(): RoutesDefinitionBuilder;
  function defineResourceRoutes(input: DefineRoutesInputLike, name?: string): RouteRegistry;
  function defineResourceRoutes(input?: DefineRoutesInputLike, name?: string): RouteRegistry | RoutesDefinitionBuilder {
    const result = defineRoutes(
      {
        name: name ?? context.name,
        resource: context,
      },
      input,
    );

    if ('ref' in result) {
      routeRegistries.push(result);
      Object.assign(routes.ref, result.ref);
      return result;
    }

    return {
      params(parameters) {
        result.params(parameters);
        return this;
      },
      routes(routeInput) {
        const registry = result.routes(routeInput);
        routeRegistries.push(registry);
        Object.assign(routes.ref, registry.ref);
        return registry;
      },
    } satisfies typeof result;
  }

  function setInfo(info: InfoInput): ResourceBuilder {
    const next = normalizeInfo(info);
    (context as ResourceContext & { info?: ReturnType<typeof normalizeInfo> }).info = normalizeInfo([
      ...(context.info ? [context.info] : []),
      ...(next ? [next] : []),
    ]);
    return resourceBuilder;
  }

  const resourceBuilder: ResourceBuilder = {
    context,
    properties,
    schemas,
    schemaComponents,
    parameterComponents,
    requestBodyComponents,
    responseComponents,
    accessComponents,
    hookComponents,
    entityComponents,
    entityRelationComponents,
    routeRegistries,
    routes,
    access,
    defineProperties: defineResourceProperties,
    defineSchemas: defineResourceSchemas,
    defineParameters: defineResourceParameters,
    defineRequestBodies: defineResourceRequestBodies,
    defineResponses: defineResourceResponses,
    defineAccess: defineResourceAccess,
    defineHooks: defineResourceHooks,
    defineEntities: defineResourceEntities,
    defineEntityRelations: defineResourceEntityRelations,
    defineRoutes: defineResourceRoutes,
    info: setInfo,
  };

  return resourceBuilder;
}
