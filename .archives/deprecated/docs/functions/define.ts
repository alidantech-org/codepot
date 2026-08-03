// import { z, ZodTypeAny, ZodObject, ZodRawShape } from 'zod';

// // ============================================================================
// // CORE TYPES (from our design)
// // ============================================================================

// export interface DefinitionItem {
//   description?: string;
//   deprecated?: boolean;
//   meta?: Record<string, unknown>;
// }

// export type Ref<T> = string & { readonly __type: T };

// export function ref<T>(path: string): Ref<T> {
//   return path as Ref<T>;
// }

// // ============================================================================
// // ENUMS
// // ============================================================================

// export const HttpMethod = {
//   get: 'get',
//   post: 'post',
//   put: 'put',
//   patch: 'patch',
//   delete: 'delete',
//   options: 'options',
//   head: 'head',
// } as const;
// export type HttpMethod = (typeof HttpMethod)[keyof typeof HttpMethod];

// export const QueryOperator = {
//   eq: 'eq',
//   neq: 'neq',
//   in: 'in',
//   notIn: 'notIn',
//   contains: 'contains',
//   startsWith: 'startsWith',
//   endsWith: 'endsWith',
//   gt: 'gt',
//   gte: 'gte',
//   lt: 'lt',
//   lte: 'lte',
//   between: 'between',
//   exists: 'exists',
// } as const;
// export type QueryOperator = (typeof QueryOperator)[keyof typeof QueryOperator];

// export const FieldAccessLevel = {
//   public: 'public',
//   internal: 'internal',
//   secret: 'secret',
//   auth: 'auth',
// } as const;
// export type FieldAccessLevel = (typeof FieldAccessLevel)[keyof typeof FieldAccessLevel];

// export const FieldPersistenceMode = {
//   stored: 'stored',
//   virtual: 'virtual',
//   computed: 'computed',
// } as const;
// export type FieldPersistenceMode = (typeof FieldPersistenceMode)[keyof typeof FieldPersistenceMode];

// export const UrlEnv = {
//   local: 'local',
//   development: 'development',
//   staging: 'staging',
//   production: 'production',
// } as const;
// export type UrlEnv = (typeof UrlEnv)[keyof typeof UrlEnv];

// export const ContentTypeStrategy = {
//   json: 'json',
//   xml: 'xml',
//   yaml: 'yaml',
//   html: 'html',
//   csv: 'csv',
//   multipart: 'multipart',
//   form: 'form',
//   urlencoded: 'urlencoded',
//   text: 'text',
//   binary: 'binary',
//   stream: 'stream',
//   graphql: 'graphql',
//   protobuf: 'protobuf',
//   msgpack: 'msgpack',
// } as const;
// export type ContentTypeStrategy = (typeof ContentTypeStrategy)[keyof typeof ContentTypeStrategy];

// // ============================================================================
// // FIELD TYPES
// // ============================================================================

// export interface FieldQueryConfig {
//   filter?: boolean;
//   sort?: boolean;
//   select?: boolean;
//   operators?: QueryOperator[];
// }

// export interface FieldAccessConfig {
//   read?: FieldAccessLevel;
//   write?: FieldAccessLevel;
//   sensitive?: boolean;
// }

// export interface FieldPersistenceConfig {
//   mode: FieldPersistenceMode;
//   generated?: boolean;
//   immutable?: boolean;
// }

// export interface EntityFieldConfig {
//   schema?: ZodTypeAny;
//   ref?: PrimitiveRef;
//   required?: boolean;
//   nullable?: boolean;
//   default?: unknown;
//   description?: string;
//   query?: FieldQueryConfig & { select?: boolean };
//   access?: FieldAccessConfig | FieldAccessLevel;
//   persistence?: FieldPersistenceConfig;
// }

// // ============================================================================
// // PRIMITIVE
// // ============================================================================

// export interface PrimitiveDefinition extends DefinitionItem {
//   schema: ZodTypeAny;
//   key: string;
//   path: string;
// }

// export interface PrimitiveRef extends PrimitiveDefinition {
//   optional(): PrimitiveRef;
//   nullable(): PrimitiveRef;
//   array(): PrimitiveRef;
// }

// function makePrimitiveRef(def: PrimitiveDefinition): PrimitiveRef {
//   return {
//     ...def,
//     optional() {
//       return makePrimitiveRef({ ...def, schema: def.schema.optional() });
//     },
//     nullable() {
//       return makePrimitiveRef({ ...def, schema: def.schema.nullable() });
//     },
//     array() {
//       return makePrimitiveRef({ ...def, schema: def.schema.array() });
//     },
//   };
// }

// // ============================================================================
// // ENTITY
// // ============================================================================

// export interface EntityModels {
//   public: ZodObject<ZodRawShape>;
//   create: ZodObject<ZodRawShape>;
//   patch: ZodObject<ZodRawShape>;
//   query: {
//     filter: ZodObject<ZodRawShape>;
//     sort: ZodTypeAny;
//     select: ZodTypeAny;
//   };
//   internal: ZodObject<ZodRawShape>;
// }

// export interface EntityDefinition<TFields extends Record<string, EntityFieldConfig>> extends DefinitionItem {
//   key: string;
//   fields: { [K in keyof TFields]: PrimitiveRef };
//   models: EntityModels;
//   abstract?: boolean;
// }

// function resolveFieldSchema(cfg: EntityFieldConfig): ZodTypeAny {
//   let schema = cfg.ref?.schema ?? cfg.schema ?? z.unknown();
//   if (cfg.nullable) schema = schema.nullable();
//   if (cfg.required === false) schema = schema.optional();
//   return schema;
// }

// function resolveAccess(access: EntityFieldConfig['access']): FieldAccessConfig {
//   if (!access) return {};
//   if (typeof access === 'string') return { read: access as FieldAccessLevel };
//   return access;
// }

// function buildEntityModels<TFields extends Record<string, EntityFieldConfig>>(
//   fields: TFields,
//   extendsEntity?: EntityDefinition<any>,
// ): EntityModels {
//   const allFields = {
//     ...(extendsEntity ? Object.fromEntries(Object.entries(extendsEntity.fields).map(([k, v]) => [k, { schema: v.schema }])) : {}),
//     ...fields,
//   };

//   const publicShape: Record<string, ZodTypeAny> = {};
//   const createShape: Record<string, ZodTypeAny> = {};
//   const patchShape: Record<string, ZodTypeAny> = {};
//   const filterShape: Record<string, ZodTypeAny> = {};
//   const internalShape: Record<string, ZodTypeAny> = {};
//   const sortKeys: string[] = [];
//   const selectKeys: string[] = [];

//   for (const [key, cfg] of Object.entries(allFields)) {
//     const access = resolveAccess(cfg.access);
//     const schema = resolveFieldSchema(cfg);
//     const isSecret = access.read === 'secret' || access.sensitive;
//     const isInternal = access.read === 'internal' || access.read === 'auth';
//     const isSelectOff = (cfg.query as any)?.select === false;
//     const isStored = cfg.persistence?.mode !== 'computed' && cfg.persistence?.mode !== 'virtual';
//     const isImmutable = cfg.persistence?.immutable;

//     // public model: not secret, not internal
//     if (!isSecret && !isInternal) publicShape[key] = schema;

//     // internal model: everything except secret
//     if (!isSecret) internalShape[key] = schema;

//     // create: stored, writable, not generated
//     if (isStored && access.write !== 'secret' && !cfg.persistence?.generated) {
//       createShape[key] = cfg.required === false ? schema.optional() : schema;
//     }

//     // patch: create fields minus immutable
//     if (key in createShape && !isImmutable) {
//       patchShape[key] = schema.optional();
//     }

//     // query models
//     if (cfg.query?.filter) filterShape[key] = schema.optional();
//     if (cfg.query?.sort) sortKeys.push(key);
//     if (cfg.query?.select !== false && !isSelectOff && !isSecret) selectKeys.push(key);
//   }

//   const sortEnum = sortKeys.length ? z.enum(sortKeys as [string, ...string[]]).optional() : z.never();
//   const selectEnum = selectKeys.length ? z.enum(selectKeys as [string, ...string[]]).optional() : z.never();

//   return {
//     public: z.object(publicShape as ZodRawShape),
//     create: z.object(createShape as ZodRawShape),
//     patch: z.object(patchShape as ZodRawShape),
//     internal: z.object(internalShape as ZodRawShape),
//     query: {
//       filter: z.object(filterShape as ZodRawShape),
//       sort: sortEnum,
//       select: selectEnum,
//     },
//   };
// }

// // ============================================================================
// // SCHEMA BUILDER (extendable schemas)
// // ============================================================================

// export interface SchemaRef {
//   _schema: ZodTypeAny;
//   optional(): SchemaRef;
//   nullable(): SchemaRef;
//   array(): SchemaRef;
//   extend(shape: Record<string, SchemaRef | PrimitiveRef | ZodTypeAny>): SchemaRef;
// }

// function makeSchemaRef(schema: ZodTypeAny): SchemaRef {
//   return {
//     _schema: schema,
//     optional() {
//       return makeSchemaRef(schema.optional());
//     },
//     nullable() {
//       return makeSchemaRef(schema.nullable());
//     },
//     array() {
//       return makeSchemaRef(schema.array());
//     },
//     extend(shape) {
//       const base = schema instanceof ZodObject ? schema : z.object({});
//       const resolved: Record<string, ZodTypeAny> = {};
//       for (const [k, v] of Object.entries(shape)) {
//         resolved[k] = (v as any)._schema ?? (v as any).schema ?? v;
//       }
//       return makeSchemaRef(base.extend(resolved as ZodRawShape));
//     },
//   };
// }

// function resolveSchemaShape(shape: Record<string, SchemaRef | PrimitiveRef | ZodTypeAny>): ZodObject<ZodRawShape> {
//   const resolved: Record<string, ZodTypeAny> = {};
//   for (const [k, v] of Object.entries(shape)) {
//     resolved[k] = (v as any)._schema ?? (v as any).schema ?? v;
//   }
//   return z.object(resolved as ZodRawShape);
// }

// // ============================================================================
// // ROUTE TYPES
// // ============================================================================

// export interface RouteDefinition {
//   method: HttpMethod;
//   path: string;
//   summary?: string;
//   description?: string;
//   query?: SchemaRef | ZodTypeAny;
//   body?: SchemaRef | ZodTypeAny;
//   response?: Record<number, SchemaRef | ZodTypeAny>;
//   security?: { protected?: boolean; roles?: string[] };
// }

// export interface RoutesConfig {
//   params?: Record<string, PrimitiveRef>;
//   [routeKey: string]: RouteDefinition | Record<string, PrimitiveRef> | undefined;
// }

// // ============================================================================
// // RESOURCE
// // ============================================================================

// export interface ResourceInstance<
//   TPrimitives extends Record<string, PrimitiveDefinition> = {},
//   TEntities extends Record<string, EntityDefinition<any>> = {},
//   TSchemas extends Record<string, SchemaRef> = {},
// > {
//   key: string;
//   primitives<TDefs extends Record<string, { schema: ZodTypeAny; description?: string; required?: boolean }>>(
//     name: string,
//     defs: TDefs,
//   ): { [K in keyof TDefs]: PrimitiveRef };

//   entity<TType = unknown>(): <TFields extends Record<string, EntityFieldConfig>>(
//     name: string,
//     config: { fields: TFields; extends?: EntityDefinition<any>; abstract?: boolean },
//   ) => EntityDefinition<TFields>;

//   schemas<TDefs extends Record<string, Record<string, SchemaRef | PrimitiveRef | ZodTypeAny> | SchemaRef>>(
//     defs: TDefs,
//   ): { [K in keyof TDefs]: SchemaRef };

//   routes(config: RoutesConfig): void;
// }

// function createResource(key: string, config: { route?: string; folders?: string[]; description?: string }): ResourceInstance {
//   const resourceData: any = {
//     key,
//     route: config.route,
//     folders: config.folders,
//     description: config.description,
//     primitives: {},
//     entities: {},
//     schemas: {},
//     routes: {},
//   };

//   return {
//     key,

//     primitives(name, defs) {
//       const result: Record<string, PrimitiveRef> = {};
//       for (const [k, cfg] of Object.entries(defs)) {
//         const path = `${key}.primitives.${name}.${k}`;
//         let schema = cfg.schema;
//         if (cfg.required === false) schema = schema.optional();
//         result[k] = makePrimitiveRef({ key: k, path, schema, description: cfg.description });
//       }
//       resourceData.primitives[name] = defs;
//       return result as any;
//     },

//     entity: () => (name, config) => {
//       const models = buildEntityModels(config.fields, config.extends);
//       const fields: Record<string, PrimitiveRef> = {};
//       for (const [k, cfg] of Object.entries(config.fields)) {
//         const path = `${key}.entities.${name}.${k}`;
//         fields[k] = makePrimitiveRef({
//           key: k,
//           path,
//           schema: resolveFieldSchema(cfg),
//           description: cfg.description,
//         });
//       }
//       // merge parent fields
//       if (config.extends) {
//         for (const [k, v] of Object.entries(config.extends.fields)) {
//           if (!fields[k]) fields[k] = v as PrimitiveRef;
//         }
//       }
//       const entity = { key: name, fields, models, abstract: config.abstract } as EntityDefinition<typeof config.fields>;
//       resourceData.entities[name] = entity;
//       return entity;
//     },

//     schemas(defs) {
//       const result: Record<string, SchemaRef> = {};
//       for (const [k, def] of Object.entries(defs)) {
//         if ((def as any)._schema) {
//           result[k] = def as SchemaRef;
//         } else {
//           result[k] = makeSchemaRef(resolveSchemaShape(def as any));
//         }
//       }
//       resourceData.schemas = defs;
//       return result as any;
//     },

//     routes(config) {
//       resourceData.routes = config;
//       resourceData.params = config.params;
//     },

//     // _getData() {
//     //   return resourceData;
//     // },
//   };
// }

// // ============================================================================
// // VERSION
// // ============================================================================

// export interface VersionDefaults {
//   requestContentType?: ContentTypeStrategy;
//   responseContentType?: ContentTypeStrategy;
//   responses?: Record<number, SchemaRef | ZodTypeAny>;
// }

// export interface VersionConfig extends DefinitionItem {
//   codepot: string;
//   key: string;
//   version: number;
//   info: {
//     title: string;
//     version: string;
//     description?: string;
//     license?: { name: string; identifier?: string; url?: string };
//     contact?: { name?: string; email?: string; url?: string };
//   };
//   urls?: Array<{ env: UrlEnv | string; uri: string }>;
//   defaults?: VersionDefaults;
// }

// export interface VersionInstance {
//   resource(config: { key: string; route?: string; folders?: string[]; description?: string }): ResourceInstance;
//   schemas<TDefs extends Record<string, Record<string, SchemaRef | PrimitiveRef | ZodTypeAny> | SchemaRef>>(
//     defs: TDefs,
//   ): { [K in keyof TDefs]: SchemaRef };
//   toJSON(): any;
// }

// export function defineVersion(config: VersionConfig): VersionInstance {
//   const resources: Record<string, ResourceInstance> = {};

//   return {
//     resource(cfg) {
//       const instance = createResource(cfg.key, cfg);
//       resources[cfg.key] = instance;
//       return instance;
//     },

//     schemas(defs) {
//       // version-level schemas (shared across resources)
//       const result: Record<string, SchemaRef> = {};
//       for (const [k, def] of Object.entries(defs)) {
//         if ((def as any)._schema) {
//           result[k] = def as SchemaRef;
//         } else {
//           result[k] = makeSchemaRef(resolveSchemaShape(def as any));
//         }
//       }
//       return result as any;
//     },

//     toJSON() {
//       return {
//         ...config,
//         resources: Object.fromEntries(
//           Object.entries(resources).map(([key, resource]) => [
//             key,
//             {
//               key: resource.key,
//               // Add serialization of primitives, entities, schemas, routes here
//             },
//           ]),
//         ),
//       };
//     },
//   };
// }

// // ============================================================================
// // SCHEMA HELPERS  (replaces old `schema.primitive` / `schema.ref`)
// // ============================================================================

// export const schema = {
//   primitive(zodSchema: ZodTypeAny, config?: Omit<EntityFieldConfig, 'schema' | 'ref'>): EntityFieldConfig {
//     return { schema: zodSchema, ...config };
//   },
//   ref(primitiveRef: PrimitiveRef, config?: Omit<EntityFieldConfig, 'schema' | 'ref'>): EntityFieldConfig {
//     return { ref: primitiveRef, ...config };
//   },
// };
