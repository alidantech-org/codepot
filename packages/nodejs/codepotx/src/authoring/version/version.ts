import { defineAccess } from '../access/access';
import type { AccessDefinitionInput } from '../access/access.types';
import { createSchemaComponentRegistry, defineParameters, defineRequestBodies, defineResponses, defineSchemas } from '../components/components';
import type { ParameterComponentInput, RequestBodyComponentInput, ResponseComponentInput, SchemaComponentValue } from '../components/component.types';
import { createAuthoringState } from '../core/normalize';
import { defineBaseEntities, defineEntities } from '../entities/entities';
import type { BaseEntityDefinitionInput, ConcreteEntityDefinitionInput, EntityDefinitionFactory } from '../entities/entity.types';
import { defineFrontend } from '../frontend/frontend';
import type { DefineFrontendOptions } from '../frontend/frontend.types';
import { defineProperties } from '../properties/define-properties';
import type { PropertyGroupOptions, PropertyRegistry, ZodPropertyDefinitionFieldMap } from '../properties/property.types';
import { defineResource } from '../resource/resource';
import type { DefineResourceOptions, ResourceBuilder } from '../resource/resource.types';
import type { RouteResponseInput } from '../routes/route.types';
import type { DefineVersionContractOptions, VersionBuilder, VersionContract } from './version.types';

export function defineVersionContract(options: DefineVersionContractOptions): VersionBuilder {
  const state = createAuthoringState();
  const rootSchemas = createSchemaComponentRegistry('shared');
  const contract: VersionContract = {
    info: options.info,
    tags: [...(options.tags ?? [])],
    defaults: { requestContentType: options.defaults?.requestContentType ?? 'application/json', responseContentType: options.defaults?.responseContentType ?? 'application/json' },
    state,
    resources: [...(options.resources ?? [])], properties: [], schemaComponents: [rootSchemas], parameterComponents: [],
    requestBodyComponents: [], responseComponents: [], accessComponents: [], baseEntityComponents: [], entityComponents: [], frontends: [], defaultResponses: {},
  };
  const builder: VersionBuilder = {
    contract, schemas: rootSchemas, properties: contract.properties, accessComponents: contract.accessComponents,
    baseEntityComponents: contract.baseEntityComponents, entityComponents: contract.entityComponents, frontends: contract.frontends,
    defineResource(resourceOptions: DefineResourceOptions): ResourceBuilder { const resource = defineResource(resourceOptions); contract.resources.push(resource); return resource; },
    addResource(resource: ResourceBuilder): VersionBuilder { contract.resources.push(resource); return builder; },
    addProperties(properties: PropertyRegistry): VersionBuilder { contract.properties.push(properties); return builder; },
    defineProperties<TName extends string, TFields extends ZodPropertyDefinitionFieldMap>(name: TName, fields: TFields, groupOptions?: PropertyGroupOptions) { const registry = defineProperties({ name: 'shared' }, name, fields, groupOptions); contract.properties.push({ name: registry.name, definitions: [...registry.definitions], ref: { [name]: registry.ref } }); return registry; },
    defineSchemas<const TInput extends Record<string, SchemaComponentValue>>(input: TInput, name?: string) { return defineSchemas({ name: name ?? 'shared', state }, input, rootSchemas); },
    defineParameters<const TInput extends Record<string, ParameterComponentInput>>(input: TInput, name?: string) { const registry = defineParameters({ name: name ?? 'shared', state }, input); contract.parameterComponents.push(registry); return registry; },
    defineRequestBodies<const TInput extends Record<string, RequestBodyComponentInput>>(input: TInput, name?: string) { const registry = defineRequestBodies({ name: name ?? 'shared', state }, input); contract.requestBodyComponents.push(registry); return registry; },
    defineResponses<const TInput extends Record<string, ResponseComponentInput>>(input: TInput, name?: string) { const registry = defineResponses({ name: name ?? 'shared', state }, input); contract.responseComponents.push(registry); return registry; },
    defineAccess<const TInput extends Record<string, AccessDefinitionInput>>(input: TInput) { const registry = defineAccess(input); contract.accessComponents.push(registry); return registry; },
    defineBaseEntities<const TInput extends Record<string, BaseEntityDefinitionInput>>(input: TInput | EntityDefinitionFactory<TInput>) { const registry = defineBaseEntities(input); contract.baseEntityComponents.push(registry); return registry; },
    defineEntities<const TInput extends Record<string, ConcreteEntityDefinitionInput>>(input: TInput | EntityDefinitionFactory<TInput>) { const registry = defineEntities({ name: 'shared' }, input); contract.entityComponents.push(registry); return registry; },
    defineFrontend(frontendOptions: DefineFrontendOptions) { if (contract.frontends.some((item) => item.context.name === frontendOptions.name)) throw new Error(`Duplicate frontend "${frontendOptions.name}".`); const frontend = defineFrontend(frontendOptions); contract.frontends.push(frontend); return frontend; },
    tags(tags: readonly string[]): VersionBuilder { contract.tags.splice(0, contract.tags.length, ...tags); return builder; },
    setDefaultResponses(responses: Record<number, RouteResponseInput>): VersionBuilder { Object.assign(contract.defaultResponses, responses); return builder; },
  };
  return builder;
}
