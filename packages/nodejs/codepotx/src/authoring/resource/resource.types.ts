import type { AccessBuilder, AccessDefinitionInput, AccessRef, AccessRegistry } from '../access/access.types';
import type { ParameterComponentInput, ParameterComponentRegistry, RequestBodyComponentInput, RequestBodyComponentRegistry, ResponseComponentInput, ResponseComponentRegistry, SchemaComponentRegistry, SchemaComponentValue } from '../components/component.types';
import type { AuthoringState, InfoInput, ResourceContext } from '../core/authoring.types';
import type { ConcreteEntityDefinitionInput, EntityDefinitionFactory, EntityRegistry, EntityRelationRegistry, EntityRelationsInput } from '../entities/entity.types';
import type { RuntimeHookDefinition, RuntimeHookRegistry } from '../hooks/hooks.types';
import type { PropertyGroupOptions, PropertyRegistry, ZodPropertyDefinitionFieldMap } from '../properties/property.types';
import type { RouteRegistry, RoutesDefinitionBuilder, DefineRoutesInput } from '../routes/route.types';

export interface DefineResourceOptions { readonly name: string; readonly route: string; readonly tag?: string; readonly tags?: readonly string[]; readonly folders?: readonly string[]; readonly alias?: string; readonly ui?: string | import('@/contract/index').JsonObject; readonly access?: AccessRef; readonly info?: InfoInput; }
export interface ResourceBuilder {
  readonly context: ResourceContext;
  readonly state: AuthoringState;
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
  readonly routes: { readonly ref: Record<string, import('../refs/ref.types').RouteRef> };
  readonly access: AccessBuilder;
  defineProperties<TName extends string, TFields extends ZodPropertyDefinitionFieldMap>(name: TName, fields: TFields, options?: PropertyGroupOptions): ReturnType<typeof import('../properties/define-properties').defineProperties<TName, TFields>>;
  defineSchemas<const TInput extends Record<string, SchemaComponentValue>>(input: TInput, name?: string): SchemaComponentRegistry<TInput>;
  defineParameters<const TInput extends Record<string, ParameterComponentInput>>(input: TInput, name?: string): ParameterComponentRegistry<TInput>;
  defineRequestBodies<const TInput extends Record<string, RequestBodyComponentInput>>(input: TInput, name?: string): RequestBodyComponentRegistry<TInput>;
  defineResponses<const TInput extends Record<string, ResponseComponentInput>>(input: TInput, name?: string): ResponseComponentRegistry<TInput>;
  defineAccess<const TInput extends Record<string, AccessDefinitionInput>>(input: TInput): AccessRegistry<TInput>;
  defineHooks<const TInput extends Record<string, RuntimeHookDefinition>>(input: TInput): RuntimeHookRegistry<TInput>;
  defineEntities<const TInput extends Record<string, ConcreteEntityDefinitionInput>>(input: TInput | EntityDefinitionFactory<TInput>): EntityRegistry<TInput>;
  defineEntityRelations(input: EntityRelationsInput): EntityRelationRegistry;
  defineRoutes(): RoutesDefinitionBuilder;
  defineRoutes(routes: DefineRoutesInput, name?: string): RouteRegistry;
  info(info: InfoInput): ResourceBuilder;
}
