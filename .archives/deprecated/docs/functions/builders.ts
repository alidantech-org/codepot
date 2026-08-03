// // ============================================================================
// // SHARED BUILDER BASE
// // ============================================================================

// import { CodepotDefinition } from '../types/definition';
// import { InfoDefinition } from '../types/info/definition';
// import { Ref } from '../types/ref';
// import { ResourceDefinition } from '../types/resource/definition';
// import { OperationInputDefinition, OperationOutputDefinition, OperationDefinition } from '../types/resource/operation/definition';
// import { RouteMethodDefinition, RoutePathDefinition, HttpMethod } from '../types/resource/route/definition';
// import { RefSchema, SchemasDefinition } from '../types/schema/definition';
// import { DtoDefinition } from '../types/schema/dto/definition';
// import { ModelDefinition, ModelCategory } from '../types/schema/model/definition';
// import { ParamsDefinition } from '../types/schema/params/definition';
// import { EntityDefinition } from '../types/schema/entity/definition';
// import { EntityField, FieldQueryConfig, FieldAccessConfig, FieldPersistenceConfig } from '../types/schema/entity/field/definition';
// import {
//   SecuritySchemeDefinition,
//   SecuritySchemeType,
//   ApiKeyLocation,
//   SecurityAuthDefinition,
//   SecurityAuthMode,
//   SecurityContextDefinition,
//   SecurityGuardDefinition,
//   RouteSecurityDefinition,
//   SecurityRoleSetDefinition,
//   SecurityRoleSourceDefinition,
//   SecurityDefinition,
// } from '../types/security/definition';
// import {
//   RequestDefinition,
//   ResponseDefinition,
//   ContentTypeDefinition,
//   ContentTypeStrategy,
//   TransportDefinition,
// } from '../types/transport/definition';
// import { UrlDefinition, UrlEnv } from '../types/url/definition';
// import { PropertiesDefinition, RefProperty } from '../types/properties/definition';
// import { PrimitiveDefinition, PrimitiveType, PrimitiveFormat } from '../types/properties/primitive/definition';
// import { EnumDefinition, EnumValueDefinition } from '../types/properties/enum/definition';
// import { CompositeDefinition } from '../types/properties/composite/definition';

// // ============================================================================
// // REF RESOLVER
// // ============================================================================

// interface RefResolverContext {
//   properties: PropertiesDefinition;
//   schemas: SchemasDefinition;
//   transport: TransportDefinition;
//   security: SecurityDefinition;
//   resources: Record<string, ResourceDefinition>;
// }

// function resolveRef<T>(ref: Ref<T>, ctx: RefResolverContext): T | string {
//   const path = ref as string;
//   const parts = path.split('.');

//   if (parts[0] === 'properties') {
//     const type = parts[1];
//     const key = parts[2];
//     if (type === 'primitives') return ctx.properties.primitives[key] as T;
//     if (type === 'enums') return ctx.properties.enums[key] as T;
//     if (type === 'composites') return ctx.properties.composites[key] as T;
//   }

//   if (parts[0] === 'schemas') {
//     const type = parts[1];
//     const key = parts[2];
//     if (type === 'entities') return ctx.schemas.entities[key] as T;
//     if (type === 'models') return ctx.schemas.models[key] as T;
//     if (type === 'dtos') return ctx.schemas.dtos[key] as T;
//     if (type === 'params') return ctx.schemas.params[key] as T;
//   }

//   if (parts[0] === 'transport') {
//     const type = parts[1];
//     const key = parts[2];
//     if (type === 'contentTypes') return ctx.transport.contentTypes[key] as T;
//     if (type === 'requests') return ctx.transport.requests[key] as T;
//     if (type === 'responses') return ctx.transport.responses[key] as T;
//   }

//   if (parts[0] === 'security') {
//     const type = parts[1];
//     const key = parts[2];
//     if (type === 'schemes') return ctx.security.schemes?.[key] as T;
//     if (type === 'auth') return ctx.security.auth?.[key] as T;
//     if (type === 'roleSources') return ctx.security.roleSources?.[key] as T;
//     if (type === 'roleSets') return ctx.security.roleSets?.[key] as T;
//     if (type === 'contexts') return ctx.security.contexts?.[key] as T;
//     if (type === 'guards') return ctx.security.guards?.[key] as T;
//   }

//   if (parts[0] === 'operations') {
//     const resourceKey = parts[1];
//     const operationKey = parts[2];
//     const resource = ctx.resources[resourceKey];
//     if (resource) {
//       // Operations are stored within routes, need to traverse
//       for (const routePath of Object.values(resource.routes || {})) {
//         for (const method of Object.values(routePath.methods || {})) {
//           if (method.operation === ref) {
//             return method as T;
//           }
//         }
//       }
//     }
//   }

//   // Return ref as string if not resolved
//   return ref;
// }

// function resolveRefsInObject(obj: any, ctx: RefResolverContext): any {
//   if (obj === null || obj === undefined) return obj;
//   if (typeof obj === 'string') {
//     // Check if it's a ref (has __type at compile time, but at runtime it's just a string)
//     // We'll assume strings with dots are refs
//     if (obj.includes('.')) {
//       return resolveRef(obj as any, ctx);
//     }
//     return obj;
//   }
//   if (Array.isArray(obj)) {
//     return obj.map((item) => resolveRefsInObject(item, ctx));
//   }
//   if (typeof obj === 'object') {
//     const result: any = {};
//     for (const [key, value] of Object.entries(obj)) {
//       result[key] = resolveRefsInObject(value, ctx);
//     }
//     return result;
//   }
//   return obj;
// }

// class Builder<T extends object> {
//   protected data: Partial<T> = {};

//   protected set<K extends keyof T>(key: K, value: T[K]): this {
//     this.data[key] = value;
//     return this;
//   }

//   description(value: string): this {
//     return this.set('description' as keyof T, value as T[keyof T]);
//   }
//   deprecated(value = true): this {
//     return this.set('deprecated' as keyof T, value as T[keyof T]);
//   }
//   meta(value: Record<string, unknown>): this {
//     return this.set('meta' as keyof T, value as T[keyof T]);
//   }

//   build(): T {
//     return this.data as T;
//   }
// }

// // ============================================================================
// // REF
// // ============================================================================

// export function ref<T>(path: string): Ref<T> {
//   return path as Ref<T>;
// }

// // ============================================================================
// // INFO
// // ============================================================================

// class InfoBuilder extends Builder<InfoDefinition> {
//   title(value: string): this {
//     return this.set('title', value);
//   }
//   version(value: string): this {
//     return this.set('version', value);
//   }
//   termsOfService(value: string): this {
//     return this.set('termsOfService', value);
//   }

//   contact(value: InfoDefinition['contact']): this {
//     return this.set('contact', value);
//   }

//   license(value: InfoDefinition['license']): this {
//     return this.set('license', value);
//   }
// }

// export function info(): InfoBuilder {
//   return new InfoBuilder();
// }

// // ============================================================================
// // URL
// // ============================================================================

// class UrlBuilder extends Builder<UrlDefinition> {
//   env(value: UrlEnv): this {
//     return this.set('env', value);
//   }
//   uri(value: string): this {
//     return this.set('uri', value);
//   }
// }

// export function url(): UrlBuilder {
//   return new UrlBuilder();
// }

// // ============================================================================
// // SECURITY SCHEME
// // ============================================================================

// class SecuritySchemeBuilder extends Builder<SecuritySchemeDefinition> {
//   type(value: SecuritySchemeType): this {
//     return this.set('type', value);
//   }
//   scheme(value: string): this {
//     return this.set('scheme', value);
//   }
//   bearerFormat(value: string): this {
//     return this.set('bearerFormat', value);
//   }
//   in(value: ApiKeyLocation): this {
//     return this.set('in', value);
//   }
//   keyName(value: string): this {
//     return this.set('keyName', value);
//   }
//   flows(value: Record<string, unknown>): this {
//     return this.set('flows', value);
//   }
//   openIdConnectUrl(value: string): this {
//     return this.set('openIdConnectUrl', value);
//   }

//   // convenience factories
//   static bearer(bearerFormat?: string): SecuritySchemeDefinition {
//     const b = new SecuritySchemeBuilder().type(SecuritySchemeType.http).scheme('bearer');
//     if (bearerFormat) b.bearerFormat(bearerFormat);
//     return b.build();
//   }

//   static apiKey(name: string, location: ApiKeyLocation): SecuritySchemeDefinition {
//     return new SecuritySchemeBuilder().type(SecuritySchemeType.apiKey).keyName(name).in(location).build();
//   }
// }

// export function securityScheme(): SecuritySchemeBuilder {
//   return new SecuritySchemeBuilder();
// }

// // ============================================================================
// // SECURITY AUTH
// // ============================================================================

// class SecurityAuthBuilder extends Builder<SecurityAuthDefinition> {
//   mode(value: SecurityAuthMode): this {
//     return this.set('mode', value);
//   }

//   scheme(schemeRef: Ref<SecuritySchemeDefinition>, scopes?: string[]): this {
//     const current = this.data.schemes ?? [];
//     this.data.schemes = [...current, { scheme: schemeRef, scopes }];
//     return this;
//   }
// }

// export function securityAuth(): SecurityAuthBuilder {
//   return new SecurityAuthBuilder();
// }

// // ============================================================================
// // SECURITY GUARD & CONTEXT
// // ============================================================================

// class SecurityContextBuilder extends Builder<SecurityContextDefinition> {
//   target(value: string): this {
//     return this.set('target', value);
//   }
//   schema(value: Ref<DtoDefinition>): this {
//     return this.set('schema', value);
//   }
// }

// class SecurityGuardBuilder extends Builder<SecurityGuardDefinition> {
//   handler(value: string): this {
//     return this.set('handler', value);
//   }
//   output(ctx: Ref<SecurityContextDefinition>): this {
//     this.data.outputs = [...(this.data.outputs ?? []), ctx];
//     return this;
//   }
// }

// export function securityContext(): SecurityContextBuilder {
//   return new SecurityContextBuilder();
// }
// export function securityGuard(): SecurityGuardBuilder {
//   return new SecurityGuardBuilder();
// }

// // ============================================================================
// // ROUTE SECURITY
// // ============================================================================

// class RouteSecurityBuilder extends Builder<RouteSecurityDefinition> {
//   protected(value = true): this {
//     return this.set('protected', value);
//   }
//   auth(value: Ref<SecurityAuthDefinition>): this {
//     return this.set('auth', value);
//   }
//   roleSet(value: Ref<SecurityRoleSetDefinition>): this {
//     this.data.roleSets = [...(this.data.roleSets ?? []), value];
//     return this;
//   }
//   guard(value: Ref<SecurityGuardDefinition>): this {
//     this.data.guards = [...(this.data.guards ?? []), value];
//     return this;
//   }
// }

// export function routeSecurity(): RouteSecurityBuilder {
//   return new RouteSecurityBuilder();
// }

// // ============================================================================
// // SECURITY DEFINITION
// // ============================================================================

// class SecurityBuilder extends Builder<SecurityDefinition> {
//   scheme(key: string, value: SecuritySchemeDefinition): this {
//     this.data.schemes = { ...(this.data.schemes ?? {}), [key]: value };
//     return this;
//   }
//   auth(key: string, value: SecurityAuthDefinition): this {
//     this.data.auth = { ...(this.data.auth ?? {}), [key]: value };
//     return this;
//   }
//   roleSource(key: string, value: SecurityRoleSourceDefinition): this {
//     this.data.roleSources = { ...(this.data.roleSources ?? {}), [key]: value };
//     return this;
//   }
//   roleSet(key: string, value: SecurityRoleSetDefinition): this {
//     this.data.roleSets = { ...(this.data.roleSets ?? {}), [key]: value };
//     return this;
//   }
//   context(key: string, value: SecurityContextDefinition): this {
//     this.data.contexts = { ...(this.data.contexts ?? {}), [key]: value };
//     return this;
//   }
//   guard(key: string, value: SecurityGuardDefinition): this {
//     this.data.guards = { ...(this.data.guards ?? {}), [key]: value };
//     return this;
//   }
//   defaults(value: RouteSecurityDefinition): this {
//     return this.set('defaults', value);
//   }
// }

// export function security(): SecurityBuilder {
//   return new SecurityBuilder();
// }

// // ============================================================================
// // PROPERTIES
// // ============================================================================

// class PrimitiveBuilder extends Builder<PrimitiveDefinition> {
//   type(value: PrimitiveType): this {
//     return this.set('type', value);
//   }
//   format(value: PrimitiveFormat): this {
//     return this.set('format', value);
//   }
//   example(value: unknown): this {
//     return this.set('example', value);
//   }
//   validation(value: PrimitiveDefinition['validation']): this {
//     return this.set('validation', value);
//   }
// }

// export function primitive(): PrimitiveBuilder {
//   return new PrimitiveBuilder();
// }

// class EnumValueBuilder extends Builder<EnumValueDefinition> {
//   value(value: EnumValueDefinition['value']): this {
//     return this.set('value', value);
//   }
//   label(value: string): this {
//     return this.set('label', value);
//   }
// }

// export function enumValue(): EnumValueBuilder {
//   return new EnumValueBuilder();
// }

// class EnumBuilder extends Builder<EnumDefinition> {
//   value(key: string, value: EnumValueDefinition): this {
//     this.data.values = { ...(this.data.values ?? {}), [key]: value };
//     return this;
//   }
// }

// export function enumDef(): EnumBuilder {
//   return new EnumBuilder();
// }

// class CompositeBuilder extends Builder<CompositeDefinition> {
//   property(key: string, value: Ref<RefProperty>): this {
//     this.data.properties = { ...(this.data.properties ?? {}), [key]: value };
//     return this;
//   }
// }

// export function composite(): CompositeBuilder {
//   return new CompositeBuilder();
// }

// class PropertiesBuilder extends Builder<PropertiesDefinition> {
//   primitive(key: string, value: PrimitiveDefinition): this {
//     this.data.primitives = { ...(this.data.primitives ?? {}), [key]: value };
//     return this;
//   }
//   enum(key: string, value: EnumDefinition): this {
//     this.data.enums = { ...(this.data.enums ?? {}), [key]: value };
//     return this;
//   }
//   composite(key: string, value: CompositeDefinition): this {
//     this.data.composites = { ...(this.data.composites ?? {}), [key]: value };
//     return this;
//   }
// }

// export function properties(): PropertiesBuilder {
//   return new PropertiesBuilder();
// }

// // ============================================================================
// // ENTITY FIELDS
// // ============================================================================

// class FieldQueryBuilder extends Builder<FieldQueryConfig> {
//   filter(value = true): this {
//     return this.set('filter', value);
//   }
//   sort(value = true): this {
//     return this.set('sort', value);
//   }
//   select(value = true): this {
//     return this.set('select', value);
//   }
// }

// export function fieldQuery(): FieldQueryBuilder {
//   return new FieldQueryBuilder();
// }

// class FieldAccessBuilder extends Builder<FieldAccessConfig> {
//   read(value: FieldAccessConfig['read']): this {
//     return this.set('read', value);
//   }
//   write(value: FieldAccessConfig['write']): this {
//     return this.set('write', value);
//   }
//   sensitive(value = true): this {
//     return this.set('sensitive', value);
//   }
// }

// export function fieldAccess(): FieldAccessBuilder {
//   return new FieldAccessBuilder();
// }

// class FieldPersistenceBuilder extends Builder<FieldPersistenceConfig> {
//   mode(value: FieldPersistenceConfig['mode']): this {
//     return this.set('mode', value);
//   }
//   generated(value = true): this {
//     return this.set('generated', value);
//   }
//   immutable(value = true): this {
//     return this.set('immutable', value);
//   }
// }

// export function fieldPersistence(): FieldPersistenceBuilder {
//   return new FieldPersistenceBuilder();
// }

// class EntityFieldBuilder extends Builder<EntityField> {
//   ref(value: Ref<RefProperty>): this {
//     return this.set('ref', value);
//   }
//   required(value = true): this {
//     return this.set('required', value);
//   }
//   nullable(value = true): this {
//     return this.set('nullable', value);
//   }
//   default(value: unknown): this {
//     return this.set('default', value);
//   }
//   query(fn: (b: FieldQueryBuilder) => FieldQueryBuilder): this {
//     return this.set('query', fn(new FieldQueryBuilder()).build());
//   }
//   access(fn: (b: FieldAccessBuilder) => FieldAccessBuilder): this {
//     return this.set('access', fn(new FieldAccessBuilder()).build());
//   }
//   persistence(fn: (b: FieldPersistenceBuilder) => FieldPersistenceBuilder): this {
//     return this.set('persistence', fn(new FieldPersistenceBuilder()).build());
//   }
// }

// export function entityField(): EntityFieldBuilder {
//   return new EntityFieldBuilder();
// }

// // ============================================================================
// // ENTITY
// // ============================================================================

// class EntityBuilder extends Builder<EntityDefinition> {
//   field(key: string, value: EntityField): this {
//     this.data.fields = { ...(this.data.fields ?? {}), [key]: value };
//     return this;
//   }
// }

// export function entity(): EntityBuilder {
//   return new EntityBuilder();
// }

// // ============================================================================
// // MODEL
// // ============================================================================

// class ModelBuilder extends Builder<ModelDefinition> {
//   from(value: Ref<EntityDefinition>): this {
//     return this.set('from', value);
//   }
//   category(value: ModelCategory): this {
//     return this.set('category', value);
//   }
//   pick(...values: string[]): this {
//     return this.set('pick', values);
//   }
//   omit(...values: string[]): this {
//     return this.set('omit', values);
//   }
//   partial(value = true): this {
//     return this.set('partial', value);
//   }
//   required(...values: string[]): this {
//     return this.set('required', values);
//   }
// }

// export function model(): ModelBuilder {
//   return new ModelBuilder();
// }

// // ============================================================================
// // DTO
// // ============================================================================

// class DtoBuilder extends Builder<DtoDefinition> {
//   extends(value: Ref<DtoDefinition | ModelDefinition>): this {
//     return this.set('extends', value);
//   }
//   field(key: string, value: Ref<RefProperty>): this {
//     this.data.fields = { ...(this.data.fields ?? {}), [key]: value };
//     return this;
//   }
//   partial(value = true): this {
//     return this.set('partial', value);
//   }
// }

// export function dto(): DtoBuilder {
//   return new DtoBuilder();
// }

// // ============================================================================
// // PARAMS
// // ============================================================================

// class ParamsBuilder extends Builder<ParamsDefinition> {
//   ref(value: Ref<PrimitiveDefinition>): this {
//     return this.set('ref', value);
//   }
//   required(value = true): this {
//     return this.set('required', value);
//   }
// }

// export function params(): ParamsBuilder {
//   return new ParamsBuilder();
// }

// // ============================================================================
// // CONTENT TYPE
// // ============================================================================

// class ContentTypeBuilder extends Builder<ContentTypeDefinition> {
//   value(value: string): this {
//     return this.set('value', value);
//   }
//   strategy(value: ContentTypeStrategy): this {
//     return this.set('strategy', value);
//   }
// }

// export function contentType(): ContentTypeBuilder {
//   return new ContentTypeBuilder();
// }

// // ============================================================================
// // TRANSPORT
// // ============================================================================

// class TransportBuilder extends Builder<TransportDefinition> {
//   contentType(key: string, value: ContentTypeDefinition): this {
//     this.data.contentTypes = { ...(this.data.contentTypes ?? {}), [key]: value };
//     return this;
//   }
//   request(key: string, value: RequestDefinition): this {
//     this.data.requests = { ...(this.data.requests ?? {}), [key]: value };
//     return this;
//   }
//   response(key: string, value: ResponseDefinition): this {
//     this.data.responses = { ...(this.data.responses ?? {}), [key]: value };
//     return this;
//   }
//   defaults(value: TransportDefinition['defaults']): this {
//     return this.set('defaults', value);
//   }
// }

// export function transport(): TransportBuilder {
//   return new TransportBuilder();
// }

// // ============================================================================
// // SCHEMAS
// // ============================================================================

// class SchemasBuilder extends Builder<SchemasDefinition> {
//   entity(key: string, value: EntityDefinition): this {
//     this.data.entities = { ...(this.data.entities ?? {}), [key]: value };
//     return this;
//   }
//   model(key: string, value: ModelDefinition): this {
//     this.data.models = { ...(this.data.models ?? {}), [key]: value };
//     return this;
//   }
//   dto(key: string, value: DtoDefinition): this {
//     this.data.dtos = { ...(this.data.dtos ?? {}), [key]: value };
//     return this;
//   }
//   params(key: string, value: ParamsDefinition): this {
//     this.data.params = { ...(this.data.params ?? {}), [key]: value };
//     return this;
//   }
// }

// export function schemas(): SchemasBuilder {
//   return new SchemasBuilder();
// }

// // ============================================================================
// // OPERATION
// // ============================================================================

// class OperationInputBuilder extends Builder<OperationInputDefinition> {
//   context(value: Ref<DtoDefinition>): this {
//     this.data.context = [...(this.data.context ?? []), value];
//     return this;
//   }
//   params(value: Ref<ParamsDefinition>): this {
//     return this.set('params', value);
//   }
//   query(value: Ref<DtoDefinition | ModelDefinition>): this {
//     return this.set('query', value);
//   }
//   body(value: Ref<DtoDefinition | ModelDefinition>): this {
//     return this.set('body', value);
//   }
// }

// class OperationOutputBuilder extends Builder<OperationOutputDefinition> {
//   result(value: Ref<DtoDefinition | ModelDefinition>): this {
//     return this.set('result', value);
//   }
//   error(value: Ref<DtoDefinition | ModelDefinition>): this {
//     this.data.errors = [...(this.data.errors ?? []), value];
//     return this;
//   }
// }

// class OperationBuilder extends Builder<OperationDefinition> {
//   input(fn: (b: OperationInputBuilder) => OperationInputBuilder): this {
//     return this.set('input', fn(new OperationInputBuilder()).build());
//   }
//   output(fn: (b: OperationOutputBuilder) => OperationOutputBuilder): this {
//     return this.set('output', fn(new OperationOutputBuilder()).build());
//   }
// }

// export function operation(): OperationBuilder {
//   return new OperationBuilder();
// }

// // ============================================================================
// // ROUTE METHOD
// // ============================================================================

// class RouteMethodBuilder extends Builder<RouteMethodDefinition> {
//   operation(value: Ref<OperationDefinition>): this {
//     return this.set('operation', value);
//   }
//   security(fn: (b: RouteSecurityBuilder) => RouteSecurityBuilder): this {
//     return this.set('security', fn(new RouteSecurityBuilder()).build());
//   }
//   query(value: Ref<RefSchema>): this {
//     return this.set('query', value);
//   }
//   body(value: RequestDefinition): this {
//     return this.set('body', value);
//   }
//   response(status: number, value: Ref<ResponseDefinition>): this {
//     this.data.responses = { ...(this.data.responses ?? {}), [status]: value };
//     return this;
//   }
// }

// export function routeMethod(): RouteMethodBuilder {
//   return new RouteMethodBuilder();
// }

// // ============================================================================
// // ROUTE PATH
// // ============================================================================

// class RoutePathBuilder extends Builder<RoutePathDefinition> {
//   param(key: string, value: Ref<ParamsDefinition>): this {
//     this.data.parameters = { ...(this.data.parameters ?? {}), [key]: value };
//     return this;
//   }
//   method(verb: HttpMethod, fn: (b: RouteMethodBuilder) => RouteMethodBuilder): this {
//     this.data.methods = {
//       ...(this.data.methods ?? {}),
//       [verb]: fn(new RouteMethodBuilder()).build(),
//     };
//     return this;
//   }

//   // convenience verbs
//   get(fn: (b: RouteMethodBuilder) => RouteMethodBuilder): this {
//     return this.method(HttpMethod.get, fn);
//   }
//   post(fn: (b: RouteMethodBuilder) => RouteMethodBuilder): this {
//     return this.method(HttpMethod.post, fn);
//   }
//   put(fn: (b: RouteMethodBuilder) => RouteMethodBuilder): this {
//     return this.method(HttpMethod.put, fn);
//   }
//   patch(fn: (b: RouteMethodBuilder) => RouteMethodBuilder): this {
//     return this.method(HttpMethod.patch, fn);
//   }
//   delete(fn: (b: RouteMethodBuilder) => RouteMethodBuilder): this {
//     return this.method(HttpMethod.delete, fn);
//   }
// }

// export function routePath(): RoutePathBuilder {
//   return new RoutePathBuilder();
// }

// // ============================================================================
// // RESOURCE
// // ============================================================================

// class ResourceBuilder extends Builder<ResourceDefinition> {
//   folders(...values: string[]): this {
//     return this.set('folders', values);
//   }
//   defaults(fn: (b: RouteSecurityBuilder) => RouteSecurityBuilder): this {
//     return this.set('defaults', { security: fn(new RouteSecurityBuilder()).build() });
//   }
//   route(path: string, fn: (b: RoutePathBuilder) => RoutePathBuilder): this {
//     this.data.routes = {
//       ...(this.data.routes ?? {}),
//       [path]: fn(new RoutePathBuilder()).build(),
//     };
//     return this;
//   }
// }

// export function resource(): ResourceBuilder {
//   return new ResourceBuilder();
// }

// // ============================================================================
// // ROOT
// // ============================================================================

// class CodepotBuilder extends Builder<CodepotDefinition> {
//   codepot(value: string): this {
//     return this.set('codepot', value);
//   }
//   key(value: string): this {
//     return this.set('key', value);
//   }
//   version(value: number): this {
//     return this.set('version', value);
//   }

//   info(fn: (b: InfoBuilder) => InfoBuilder): this {
//     return this.set('info', fn(new InfoBuilder()).build());
//   }
//   url(fn: (b: UrlBuilder) => UrlBuilder): this {
//     this.data.urls = [...(this.data.urls ?? []), fn(new UrlBuilder()).build()];
//     return this;
//   }
//   properties(fn: (b: PropertiesBuilder) => PropertiesBuilder): this {
//     return this.set('properties', fn(new PropertiesBuilder()).build());
//   }
//   schemas(fn: (b: SchemasBuilder) => SchemasBuilder): this {
//     return this.set('schemas', fn(new SchemasBuilder()).build());
//   }
//   transport(fn: (b: TransportBuilder) => TransportBuilder): this {
//     return this.set('transport', fn(new TransportBuilder()).build());
//   }
//   security(fn: (b: SecurityBuilder) => SecurityBuilder): this {
//     return this.set('security', fn(new SecurityBuilder()).build());
//   }
//   resource(key: string, fn: (b: ResourceBuilder) => ResourceBuilder): this {
//     this.data.resources = {
//       ...(this.data.resources ?? {}),
//       [key]: fn(new ResourceBuilder()).build(),
//     };
//     return this;
//   }

//   buildResolved(): CodepotDefinition {
//     const def = this.build();
//     const ctx: RefResolverContext = {
//       properties: def.properties || { primitives: {}, enums: {}, composites: {} },
//       schemas: def.schemas || { entities: {}, models: {}, dtos: {}, params: {} },
//       transport: def.transport || { contentTypes: {}, requests: {}, responses: {} },
//       security: def.security || { schemes: {}, auth: {}, roleSources: {}, roleSets: {}, contexts: {}, guards: {} },
//       resources: def.resources || {},
//     };
//     return resolveRefsInObject(def, ctx);
//   }
// }

// export function codepot(): CodepotBuilder {
//   return new CodepotBuilder();
// }
