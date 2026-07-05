import { defineResource } from '../resource/define-resource.js';
import type { DefineResourceOptions, ResourceBuilder } from '../resource/define-resource.js';
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
import type { RouteResponseInput } from '../routes/route.types.js';
import { defineProperties } from '../properties/define-properties.js';
import type { PropertyGroupOptions, PropertyRegistry, ZodPropertyDefinitionFieldMap } from '../properties/property.types.js';
import type { VersionContract, VersionInfo, VersionDefaults } from './version-contract.types.js';
import { ContentType } from '../openapi/content-type.js';
import { defineAccess } from '../access/define-access.js';
import type { AccessDefinitionInput, AccessRegistry } from '../access/access.types.js';
import { defineBaseEntities, defineEntities } from '../entities/define-entities.js';
import type { EntityDefinitionFactory } from '../entities/define-entities.js';
import type {
  BaseEntityDefinitionInput,
  ConcreteEntityDefinitionInput,
  EntityRegistry,
} from '../entities/entity.types.js';
import { defineFrontend } from '../frontend/define-frontend.js';
import type { DefineFrontendOptions, FrontendBuilder } from '../frontend/frontend.types.js';

export interface DefineVersionContractOptions {
  info: VersionInfo;
  tags?: readonly string[];
  defaults?: VersionDefaults;
  resources?: ResourceBuilder[];
  properties?: PropertyRegistry[];
  schemaComponents?: SchemaComponentRegistry[];
  parameterComponents?: ParameterComponentRegistry[];
  requestBodyComponents?: RequestBodyComponentRegistry[];
  responseComponents?: ResponseComponentRegistry[];
  accessComponents?: AccessRegistry[];
  baseEntityComponents?: EntityRegistry[];
  entityComponents?: EntityRegistry[];
  frontends?: FrontendBuilder[];
  defaultResponses?: Record<number, RouteResponseInput>;
}

export interface VersionBuilder {
  readonly contract: VersionContract;
  readonly schemas: SchemaComponentRegistry;
  readonly properties: PropertyRegistry[];
  readonly accessComponents: AccessRegistry[];
  readonly baseEntityComponents: EntityRegistry[];
  readonly entityComponents: EntityRegistry[];
  readonly frontends: FrontendBuilder[];
  defineResource(options: DefineResourceOptions): ResourceBuilder;
  addResource(resource: ResourceBuilder): VersionBuilder;
  addProperties(properties: PropertyRegistry): VersionBuilder;
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
  defineBaseEntities<const TInput extends Record<string, BaseEntityDefinitionInput>>(
    input: TInput | EntityDefinitionFactory<TInput>,
  ): EntityRegistry<TInput>;
  defineEntities<const TInput extends Record<string, ConcreteEntityDefinitionInput>>(
    input: TInput | EntityDefinitionFactory<TInput>,
  ): EntityRegistry<TInput>;
  defineFrontend(options: DefineFrontendOptions): FrontendBuilder;
  tags(tags: readonly string[]): VersionBuilder;
  setDefaultResponses(responses: Record<number, RouteResponseInput>): VersionBuilder;
}

export function defineVersionContract(options: DefineVersionContractOptions): VersionBuilder {
  const rootSchemas = createSchemaComponentRegistry('shared');
  rootSchemas.definitions.push(...(options.schemaComponents ?? []).flatMap((registry) => registry.definitions));
  Object.assign(rootSchemas.ref, ...(options.schemaComponents ?? []).map((registry) => registry.ref));

  const contract: VersionContract = {
    info: options.info,
    tags: [...(options.tags ?? [])],
    defaults: {
      requestContentType: options.defaults?.requestContentType ?? ContentType.json,
      responseContentType: options.defaults?.responseContentType ?? ContentType.json,
    },
    resources: [...(options.resources ?? [])],
    properties: [...(options.properties ?? [])],
    schemaComponents: [rootSchemas],
    parameterComponents: [...(options.parameterComponents ?? [])],
    requestBodyComponents: [...(options.requestBodyComponents ?? [])],
    responseComponents: [...(options.responseComponents ?? [])],
    accessComponents: [...(options.accessComponents ?? [])],
    baseEntityComponents: [...(options.baseEntityComponents ?? [])],
    entityComponents: [...(options.entityComponents ?? [])],
    frontends: [...(options.frontends ?? [])],
    defaultResponses: { ...(options.defaultResponses ?? {}) },
  };

  function defineVersionResource(resourceOptions: DefineResourceOptions): ResourceBuilder {
    const resource = defineResource(resourceOptions);
    contract.resources.push(resource);
    return resource;
  }

  function addResource(resource: ResourceBuilder): VersionBuilder {
    contract.resources.push(resource);
    return builder;
  }

  function addProperties(properties: PropertyRegistry): VersionBuilder {
    contract.properties.push(properties);
    return builder;
  }

  const parameterComponents = contract.parameterComponents;
  const requestBodyComponents = contract.requestBodyComponents;
  const responseComponents = contract.responseComponents;
  const accessComponents = contract.accessComponents;
  const baseEntityComponents = contract.baseEntityComponents;
  const entityComponents = contract.entityComponents;
  const frontends = contract.frontends;

  function defineVersionProperties<TName extends string, TFields extends ZodPropertyDefinitionFieldMap>(
    name: TName,
    fields: TFields,
    groupOptions?: PropertyGroupOptions,
  ) {
    const registry = defineProperties(
      {
        name: 'shared',
      },
      name,
      fields,
      groupOptions,
    );

    contract.properties.push({
      name: registry.name,
      definitions: registry.definitions,
      ref: {
        [name]: registry.ref,
      },
    });

    return registry;
  }

  const defineVersionSchemas: VersionBuilder['defineSchemas'] = <const TInput extends Record<string, SchemaComponentValue>>(
    input: TInput,
    name?: string,
  ): SchemaComponentRegistry<TInput> => {
    const registry = defineSchemas(
      {
        name: name ?? 'shared',
      },
      input,
      rootSchemas,
    ) as SchemaComponentRegistry<TInput>;

    return registry;
  };

  function defineVersionParameters<TInput extends Record<string, Omit<ParameterComponentDefinition, 'key'>>>(input: TInput, name?: string) {
    const registry = defineParameters(
      {
        name: name ?? 'shared',
      },
      input,
    );

    parameterComponents.push(registry);
    return registry;
  }

  function defineVersionRequestBodies<TInput extends Record<string, Omit<RequestBodyComponentDefinition, 'name'>>>(
    input: TInput,
    name?: string,
  ) {
    const registry = defineRequestBodies(
      {
        name: name ?? 'shared',
      },
      input,
    );

    requestBodyComponents.push(registry);
    return registry;
  }

  function defineVersionResponses<TInput extends Record<string, Omit<ResponseComponentDefinition, 'name'>>>(input: TInput, name?: string) {
    const registry = defineResponses(
      {
        name: name ?? 'shared',
      },
      input,
    );

    responseComponents.push(registry);
    return registry;
  }

  function setDefaultResponses(responses: Record<number, RouteResponseInput>): VersionBuilder {
    Object.assign(contract.defaultResponses, responses);
    return builder;
  }

  function setTags(tags: readonly string[]): VersionBuilder {
    (contract.tags as string[]).splice(0, contract.tags.length, ...tags);
    return builder;
  }

  function defineVersionAccess<const TInput extends Record<string, AccessDefinitionInput>>(input: TInput): AccessRegistry<TInput> {
    const registry = defineAccess(input);
    accessComponents.push(registry);
    return registry;
  }

  function defineVersionBaseEntities<const TInput extends Record<string, BaseEntityDefinitionInput>>(
    input: TInput | EntityDefinitionFactory<TInput>,
  ): EntityRegistry<TInput> {
    const registry = defineBaseEntities(input);
    baseEntityComponents.push(registry);
    return registry;
  }

  function defineVersionEntities<const TInput extends Record<string, ConcreteEntityDefinitionInput>>(
    input: TInput | EntityDefinitionFactory<TInput>,
  ): EntityRegistry<TInput> {
    const registry = defineEntities({ name: 'shared' }, input);
    entityComponents.push(registry);
    return registry;
  }

  function defineVersionFrontend(frontendOptions: DefineFrontendOptions): FrontendBuilder {
    if (frontends.some((frontend) => frontend.context.name === frontendOptions.name)) {
      throw new Error(`Duplicate frontend "${frontendOptions.name}". Frontend names must be unique in a version contract.`);
    }

    const frontend = defineFrontend(frontendOptions);
    frontends.push(frontend);
    return frontend;
  }

  const builder: VersionBuilder = {
    contract,
    schemas: rootSchemas,
    properties: contract.properties,
    accessComponents,
    baseEntityComponents,
    entityComponents,
    frontends,
    defineResource: defineVersionResource,
    addResource,
    addProperties,
    defineProperties: defineVersionProperties,
    defineSchemas: defineVersionSchemas,
    defineParameters: defineVersionParameters,
    defineRequestBodies: defineVersionRequestBodies,
    defineResponses: defineVersionResponses,
    defineAccess: defineVersionAccess,
    defineBaseEntities: defineVersionBaseEntities,
    defineEntities: defineVersionEntities,
    defineFrontend: defineVersionFrontend,
    tags: setTags,
    setDefaultResponses,
  };

  return builder;
}
