import {
  CODEPOT_ARTIFACT_VERSION,
  CODEPOT_PROTOCOL_VERSION,
} from '@/contract/index';
import type {
  CompiledAccessDefinition,
  CompiledAuthoringArtifact,
  CompiledDocumentation,
  CompiledEntity,
  CompiledField,
  CompiledFrontend,
  CompiledHook,
  CompiledInlineSchema,
  CompiledOperation,
  CompiledPropertyGroup,
  CompiledRelation,
  CompiledResource,
  CompiledSchema,
  CompiledSchemaUse,
  Diagnostic,
  JsonObject,
  JsonValue,
} from '@/contract/index';
import type { AccessRegistry } from '../access/access.types';
import type {
  SchemaComponentDefinition,
  SchemaComponentRegistry,
} from '../components/component.types';
import type { EntityDefinition, EntityRegistry } from '../entities/entity.types';
import type { RuntimeHookRegistry } from '../hooks/hooks.types';
import type { PropertyRegistry } from '../properties/property.types';
import { isRefUsage } from '../refs/ref-methods';
import { RefKind } from '../refs/ref-kind';
import type { EngineRef } from '../refs/ref.types';
import type { ResourceBuilder } from '../resource/resource.types';
import type { RouteDefinition } from '../routes/route.types';
import { SchemaKind } from '../schema/schema-kind';
import type { SchemaField } from '../schema/schema.types';
import type { VersionBuilder, VersionContract } from '../version/version.types';
import type {
  AuthoringCompileInput,
  AuthoringCompileOutput,
  AuthoringCompiler,
  AuthoringCompilerDependencies,
} from './compiler.types';

interface SchemaEntry {
  readonly group: string;
  readonly definition: SchemaComponentDefinition;
  readonly id: string;
}

/**
 * Internal dynamic-object view used only while normalizing user-authored values.
 * Frequently inspected properties are declared explicitly so strict index-signature
 * access remains enabled across the package.
 */
interface DynamicObject extends Record<string, unknown> {
  readonly _def?: unknown;
  readonly _zod?: unknown;
  readonly aliasOf?: unknown;
  readonly date?: unknown;
  readonly def?: unknown;
  readonly description?: unknown;
  readonly element?: unknown;
  readonly entries?: unknown;
  readonly exact?: unknown;
  readonly format?: unknown;
  readonly global?: unknown;
  readonly id?: unknown;
  readonly key?: unknown;
  readonly kind?: unknown;
  readonly mode?: unknown;
  readonly name?: unknown;
  readonly oneOf?: unknown;
  readonly owner?: unknown;
  readonly range?: unknown;
  readonly required?: unknown;
  readonly resource?: unknown;
  readonly safeParse?: unknown;
  readonly schema?: unknown;
  readonly search?: unknown;
  readonly sort?: unknown;
  readonly source?: unknown;
  readonly sourceRefId?: unknown;
  readonly summary?: unknown;
  readonly type?: unknown;
  readonly typeName?: unknown;
  readonly value?: unknown;
  readonly values?: unknown;
}

/** Compiles user builders into the stable, JSON-safe authoring artifact. */
export class DefaultAuthoringCompiler implements AuthoringCompiler {
  readonly #dependencies: AuthoringCompilerDependencies;

  constructor(dependencies: AuthoringCompilerDependencies) {
    this.#dependencies = dependencies;
  }

  async compile(input: AuthoringCompileInput): Promise<AuthoringCompileOutput> {
    const diagnostics: Diagnostic[] = [];
    const contracts = input.config.contracts.map(toContract);

    if (contracts.length === 0) {
      diagnostics.push(diagnostic(
        'AUTHORING_NO_CONTRACTS',
        'error',
        'codepotx.config.ts must define at least one contract.',
      ));
    }

    const properties = contracts.flatMap((contract) => compileProperties(contract.properties));
    const schemas = compileSchemas(collectSchemas(contracts));
    const schemaFields = new Map<string, readonly CompiledField[]>(
      schemas.map((schema) => [
        schema.id,
        schema.schema.kind === 'object' ? schema.schema.fields : [],
      ]),
    );
    const entities = contracts.flatMap((contract) => [
      ...compileEntities(contract.baseEntityComponents, schemaFields),
      ...compileEntities(contract.entityComponents, schemaFields),
      ...contract.resources.flatMap((resource) =>
        compileEntities(resource.entityComponents, schemaFields),
      ),
    ]);
    const relations: CompiledRelation[] = contracts.flatMap((contract) =>
      contract.resources.flatMap((resource) =>
        resource.entityRelationComponents.flatMap((registry) =>
          registry.definitions.map(compileRelation),
        ),
      ),
    );
    const access = contracts.flatMap((contract) => [
      ...compileAccess(contract.accessComponents),
      ...contract.resources.flatMap((resource) =>
        compileAccess(resource.accessComponents),
      ),
    ]);
    const hooks = contracts.flatMap((contract) =>
      contract.resources.flatMap((resource) =>
        compileHooks(resource.hookComponents),
      ),
    );
    const frontends: CompiledFrontend[] = contracts.flatMap((contract) =>
      contract.frontends.map((frontend) => ({
        id: `frontend:${frontend.context.name}`,
        key: frontend.context.name,
        name: frontend.context.name,
        components: frontend.components,
        screens: frontend.screens,
        ...docsProperty(frontend.context.info),
        ...(frontend.context.metadata
          ? { metadata: frontend.context.metadata }
          : {}),
      })),
    );

    const resources: CompiledResource[] = [];
    const operations: CompiledOperation[] = [];
    for (const contract of contracts) {
      for (const resource of contract.resources) {
        const compiled = compileResource(resource, contract, diagnostics);
        resources.push(compiled.resource);
        operations.push(...compiled.operations);
      }
    }

    validateOperations(operations, diagnostics);

    const first = contracts[0];
    const body = {
      source: input.source,
      project: {
        name: first?.info.title ?? 'Codepot',
        version: first?.info.version ?? '0.0.0',
        ...(first?.info.description ? { description: first.info.description } : {}),
        ...(first?.info.license ? { license: jsonObject(first.info.license) } : {}),
        tags: [...new Set(contracts.flatMap((contract) => contract.tags))],
        defaults: jsonObject(first?.defaults ?? {}),
        ...(input.config.metadata ? { metadata: input.config.metadata } : {}),
      },
      properties,
      schemas,
      entities,
      relations,
      resources,
      operations,
      access,
      hooks,
      frontends,
      metadata: {
        contractCount: contracts.length,
        ...(input.includeDebugMetadata ? { debug: true } : {}),
      },
      diagnostics,
    };
    const contentDigest = await this.#dependencies.hash.text(JSON.stringify(body));
    const artifact: CompiledAuthoringArtifact = {
      header: {
        kind: 'codepot.authoring',
        protocolVersion: CODEPOT_PROTOCOL_VERSION,
        artifactVersion: CODEPOT_ARTIFACT_VERSION,
        producer: { name: 'codepotx', version: '0.0.0' },
        contentDigest,
        sourceDigest: input.source.digest,
      },
      ...body,
    };

    return { artifact, diagnostics };
  }
}

function toContract(value: VersionBuilder | VersionContract): VersionContract {
  return 'contract' in value ? value.contract : value;
}

function collectSchemas(contracts: readonly VersionContract[]): SchemaEntry[] {
  const output: SchemaEntry[] = [];
  const append = (registry: SchemaComponentRegistry): void => {
    for (const definition of registry.definitions) {
      output.push({
        group: registry.name,
        definition,
        id: registry.ref[definition.name]?.id
          ?? `component:schema:${definition.name}`,
      });
    }
  };

  for (const contract of contracts) {
    contract.schemaComponents.forEach(append);
    for (const resource of contract.resources) {
      resource.schemaComponents.forEach(append);
    }
  }
  return output;
}

function compileProperties(
  registries: readonly PropertyRegistry[],
): CompiledPropertyGroup[] {
  return registries.flatMap((registry) =>
    registry.definitions.map((definition) => ({
      id: `property-group:${registry.name}:${definition.name}`,
      key: definition.name,
      name: definition.name,
      properties: Object.entries(definition.fields).map(([key, value]) =>
        field(
          key,
          value,
          propertyRefId(registry, key)
            ?? `property:${definition.name}:${key}`,
        ),
      ),
      metadata: jsonObject({
        kind: definition.kind,
        emitSchema: definition.emitSchema ?? null,
        abstract: definition.abstract ?? null,
      }),
    })),
  );
}

function propertyRefId(
  registry: PropertyRegistry,
  key: string,
): string | undefined {
  const candidate = registry.ref[key];
  return dynamicObject(candidate) && typeof candidate.id === 'string'
    ? candidate.id
    : undefined;
}

function compileSchemas(entries: readonly SchemaEntry[]): CompiledSchema[] {
  return entries.map(({ group, definition, id }) => ({
    id,
    key: definition.name,
    name: definition.name,
    group,
    schema: namedSchema(definition.value),
    ...docsProperty(definition.info),
    ...(definition.projection
      ? { metadata: jsonObject({ projection: definition.projection }) }
      : {}),
  }));
}

function namedSchema(value: unknown): CompiledInlineSchema {
  if (isProjection(value)) {
    return {
      kind: 'object',
      fields: [],
      extends: [value.sourceRefId],
      additionalProperties: false,
      metadata: jsonObject({
        projection: {
          source: value.source,
          mode: value.mode,
          fields: value.fields ?? [],
          steps: value.steps ?? [],
        },
      }),
    };
  }
  if (isRef(value)) {
    return {
      kind: 'object',
      fields: [],
      extends: [refId(value)],
      additionalProperties: false,
    };
  }
  if (isSchemaField(value)) return inlineSchema(value);
  if (dynamicObject(value) && !isZod(value)) return objectSchema(value);
  return zodSchema(value);
}

function compileRelation(
  relation: Parameters<
    typeof Array.prototype.map<CompiledRelation>
  >[0] extends (value: infer TValue, ...rest: never[]) => unknown ? TValue : never,
): CompiledRelation {
  const value = relation as {
    readonly source: string;
    readonly name: string;
    readonly target: { readonly id: string };
    readonly local: string;
    readonly foreign: string;
    readonly cardinality: string;
    readonly onDelete?: unknown;
  };
  const behavior = deleteBehavior(value.onDelete);
  return {
    id: `relation:${value.source}:${value.name}`,
    key: value.name,
    name: value.name,
    sourceEntity: value.source,
    targetEntity: value.target.id,
    sourceField: value.local,
    targetField: value.foreign,
    cardinality: cardinality(value.cardinality),
    required: dynamicObject(value.onDelete)?.setNull !== true,
    ...(behavior ? { deleteBehavior: behavior } : {}),
  };
}

function compileEntities(
  registries: readonly EntityRegistry[],
  schemaFields: ReadonlyMap<string, readonly CompiledField[]>,
): CompiledEntity[] {
  return registries.flatMap((registry) =>
    registry.definitions.map((definition) =>
      compileEntity(definition, schemaFields),
    ),
  );
}

function compileEntity(
  definition: EntityDefinition,
  schemaFields: ReadonlyMap<string, readonly CompiledField[]>,
): CompiledEntity {
  const source = schemaFields.get(definition.schema.id) ?? [];
  const fields = source.map((item) => {
    const metadata = definition.fields[item.key];
    if (!metadata) return item;
    return {
      ...item,
      lifecycle: {
        selectable: metadata.select !== false,
        editable: metadata.edit !== false
          && metadata.readonly !== true
          && metadata.managed !== true,
        immutable: metadata.immutable === true,
        managed: metadata.managed === true || metadata.readonly === true,
      },
      query: queryMetadata(metadata.query),
      metadata: jsonObject({
        index: metadata.index ?? false,
        unique: metadata.unique ?? false,
        role: metadata.role ?? null,
        generated: metadata.generated ?? null,
      }),
    } satisfies CompiledField;
  });

  return {
    id: definition.ref.id,
    key: definition.key,
    name: definition.key,
    entityKind: definition.kind === 'abstract' ? 'base' : 'concrete',
    fields,
    ...(definition.extends ? { extends: definition.extends.id } : {}),
    constraints: Object.entries(definition.constraints ?? {}).map(
      ([key, constraint]) => ({
        id: `entity-constraint:${definition.ref.id}:${key}`,
        kind: constraint.kind,
        fields: constraint.fields ?? [],
        rules: constraint.rule ? [jsonObject(constraint.rule)] : [],
      }),
    ),
    relationIds: [],
    ...(definition.store ? { owner: definition.store } : {}),
    ...docsProperty(definition.info),
  };
}

function compileAccess(
  registries: readonly AccessRegistry[],
): CompiledAccessDefinition[] {
  return registries.flatMap((registry) =>
    registry.definitions.map((definition) => ({
      id: `access:${owner(definition.owner)}:${definition.key}`,
      key: definition.key,
      name: definition.key,
      owner: owner(definition.owner),
      roleSources: Object.entries(definition.roles ?? {}).map(
        ([key, role]) => jsonObject({
          key,
          source: role.source.id,
          allow: role.allow,
        }),
      ),
      allow: jsonObject({
        context: definition.context?.id ?? null,
        roles: Object.fromEntries(
          Object.entries(definition.roles ?? {}).map(
            ([key, role]) => [key, role.allow],
          ),
        ),
        tags: definition.tags ?? [],
      }),
      ...docsProperty(definition.info),
    })),
  );
}

function compileHooks(registries: readonly RuntimeHookRegistry[]): CompiledHook[] {
  return registries.flatMap((registry) =>
    registry.definitions.map((definition) => ({
      id: `hook:${owner(definition.owner)}:${definition.key}`,
      key: definition.key,
      name: definition.key,
      owner: owner(definition.owner),
      phase: definition.phase,
      ...(definition.transport ? { transport: 'runtime' } : {}),
      ...(definition.transport?.inbound
        ? { inbound: jsonObject(definition.transport.inbound) }
        : {}),
      ...(definition.transport?.outbound
        ? { outbound: jsonObject(definition.transport.outbound) }
        : {}),
      ...docsProperty(definition.info),
    })),
  );
}

function compileResource(
  resource: ResourceBuilder,
  contract: VersionContract,
  diagnostics: Diagnostic[],
): { readonly resource: CompiledResource; readonly operations: readonly CompiledOperation[] } {
  const operations = resource.routeRegistries.flatMap((registry) =>
    Object.entries(registry.routes).map(([key, route]) =>
      compileOperation(key, route, resource, contract, diagnostics),
    ),
  );
  const resourceAccessRef = accessRef(resource.context.access);

  return {
    resource: {
      id: `resource:${resource.context.name}`,
      key: resource.context.name,
      name: resource.context.alias,
      route: resource.context.route,
      folders: resource.context.folders,
      tags: resource.context.tags,
      operationIds: operations.map((operation) => operation.id),
      ...(resourceAccessRef ? { accessRef: resourceAccessRef } : {}),
      hookRefs: resource.hookComponents.flatMap((registry) =>
        registry.definitions.map((hook) =>
          `hook:${owner(hook.owner)}:${hook.key}`,
        ),
      ),
      ...(resource.context.ui ? { frontend: resource.context.ui } : {}),
      ...docsProperty(resource.context.info),
    },
    operations,
  };
}

function compileOperation(
  key: string,
  route: RouteDefinition,
  resource: ResourceBuilder,
  contract: VersionContract,
  diagnostics: Diagnostic[],
): CompiledOperation {
  const operationId = route.operationId ?? key;
  const path = joinPath(resource.context.route, route.path);
  const responses = new Map<number, unknown>();
  for (const [status, response] of Object.entries(contract.defaultResponses)) {
    responses.set(Number(status), response);
  }
  for (const [status, response] of Object.entries(route.responses ?? {})) {
    responses.set(Number(status), response);
  }
  if (route.response) responses.set(200, route.response);
  if (responses.size === 0) {
    diagnostics.push(diagnostic(
      'AUTHORING_OPERATION_NO_RESPONSE',
      'warning',
      `Operation ${operationId} does not declare a response.`,
    ));
  }

  return {
    id: `operation:${operationId}`,
    key,
    name: operationId,
    operationId,
    resourceId: `resource:${resource.context.name}`,
    method: route.method,
    path,
    tags: [...new Set([...resource.context.tags, ...(route.tags ?? [])])],
    parameters: pathParameters(path),
    ...(route.body
      ? {
          requestBody: {
            id: `request-body:${operationId}`,
            key: `${operationId}:body`,
            name: `${operationId}:body`,
            required: required(route.body),
            content: [{
              mediaType: 'application/json',
              schema: schemaUse(bodySchema(route.body)),
            }],
          },
        }
      : {}),
    responses: [...responses.entries()]
      .sort(([left], [right]) => left - right)
      .map(([status, response]) => ({
        id: `response:${operationId}:${status}`,
        key: String(status),
        name: String(status),
        status,
        content: noContent(response)
          ? []
          : [{ mediaType: 'application/json', schema: schemaUse(responseSchema(response)) }],
        headers: [],
      })),
    ...(route.access
      ? { accessRef: `access:${owner(route.access.owner)}:${route.access.key}` }
      : {}),
    hookRefs: Object.values(route.runtime?.hooks ?? {}).map((hook) =>
      `hook:${owner(hook.definition.owner)}:${hook.key}`,
    ),
    effects: Object.entries(route.effects ?? {}).map(([kind, value]) => ({
      kind,
      value: jsonValue(value),
    })),
    cacheInvalidates: route.cache?.invalidate?.operations ?? [],
    ...docsProperty(route.info),
    metadata: jsonObject({
      codegenTags: route.codegenTags ?? [],
      meta: route.meta ?? {},
      ui: route.ui ?? null,
      sources: route.sources ?? {},
    }),
  };
}

function pathParameters(path: string): CompiledOperation['parameters'] {
  return Array.from(path.matchAll(/:([A-Za-z_][A-Za-z0-9_]*)/g), (match) => match[1])
    .filter((name): name is string => name !== undefined)
    .map((name) => ({
      id: `parameter:path:${name}`,
      key: name,
      name,
      location: 'path',
      schema: inlineUse({ kind: 'primitive', primitive: 'string', constraints: [] }),
      required: true,
    }));
}

function field(key: string, value: unknown, id: string): CompiledField {
  return {
    id,
    key,
    name: key,
    wireName: key,
    schema: schemaUse(value),
    lifecycle: {
      selectable: true,
      editable: true,
      immutable: false,
      managed: false,
    },
    query: queryMetadata(undefined),
  };
}

function schemaUse(value: unknown): CompiledSchemaUse {
  const usage = isRefUsage(value) ? value.usage : undefined;
  const source = isRefUsage(value) ? value.ref : value;
  const requiredValue = usage?.required ?? true;
  const nullable = usage?.nullable ?? false;
  const base = isEngineRef(source)
    ? ({ kind: 'ref', ref: source.id, required: requiredValue, nullable } as const)
    : ({
        kind: 'inline',
        schema: isSchemaField(source)
          ? inlineSchema(source)
          : dynamicObject(source) && !isZod(source)
            ? objectSchema(source)
            : zodSchema(source),
        required: requiredValue,
        nullable,
      } as const);

  if (!usage?.array) return base;
  return inlineUse({ kind: 'array', items: base, constraints: [] }, requiredValue, nullable);
}

function inlineSchema(value: SchemaField): CompiledInlineSchema {
  switch (value.kind) {
    case SchemaKind.primitive:
      return zodSchema(value.zod);
    case SchemaKind.composite:
      return objectSchema(value.fields);
    case SchemaKind.ref:
      return {
        kind: 'object',
        fields: [],
        extends: [refId(value.ref)],
        additionalProperties: false,
      };
    case SchemaKind.record:
      return { kind: 'record', values: schemaUse(value.value) };
    case SchemaKind.literal:
      return { kind: 'literal', value: value.value };
    case SchemaKind.oneOf:
      return {
        kind: 'union',
        mode: 'oneOf',
        variants: value.values.map(schemaUse),
      };
    case SchemaKind.anyOf:
      return {
        kind: 'union',
        mode: 'anyOf',
        variants: value.values.map(schemaUse),
      };
    case SchemaKind.file:
      return { kind: 'file', mediaTypes: ['application/octet-stream'] };
    case SchemaKind.noContent:
      return { kind: 'noContent' };
  }
}

function objectSchema(value: Readonly<Record<string, unknown>>): CompiledInlineSchema {
  return {
    kind: 'object',
    fields: Object.entries(value).map(([key, item]) =>
      field(key, item, isRef(item) ? refId(item) : `field:${key}`),
    ),
    extends: [],
    additionalProperties: false,
  };
}

function zodSchema(value: unknown): CompiledInlineSchema {
  if (!isZod(value)) {
    return { kind: 'primitive', primitive: primitive(value), constraints: [] };
  }
  const definition = zodDefinition(value);
  const kind = String(
    definition.type ?? definition.typeName ?? value.constructor.name,
  ).toLowerCase();
  if (kind.includes('array')) {
    return {
      kind: 'array',
      items: inlineUse(zodSchema(definition.element ?? definition.type)),
      constraints: [],
    };
  }
  if (kind.includes('enum')) {
    const entries = dynamicObject(definition.entries) ? definition.entries : {};
    const values = Object.values(entries).filter(
      (item): item is string | number =>
        typeof item === 'string' || typeof item === 'number',
    );
    return {
      kind: 'enum',
      valueType: values.some((item) => typeof item === 'number')
        ? 'number'
        : 'string',
      options: values.map((item) => ({ key: String(item), value: item })),
    };
  }
  if (kind.includes('literal')) {
    return {
      kind: 'literal',
      value: jsonValue(
        definition.value
          ?? (Array.isArray(definition.values) ? definition.values[0] : null),
      ),
    };
  }
  return {
    kind: 'primitive',
    primitive: kind.includes('string')
      ? 'string'
      : kind.includes('boolean')
        ? 'boolean'
        : kind.includes('bigint')
          ? 'bigint'
          : kind.includes('int')
            ? 'integer'
            : kind.includes('number')
              ? 'number'
              : kind.includes('date')
                ? 'date'
                : 'unknown',
    constraints: [],
    ...(typeof definition.format === 'string'
      ? { format: definition.format }
      : {}),
  };
}

function queryMetadata(value: unknown): CompiledField['query'] {
  const query = dynamicObject(value) ? value : {};
  const operators = [
    query.exact ? 'exact' : undefined,
    query.oneOf ? 'oneOf' : undefined,
    query.range ? 'range' : undefined,
    query.date ? 'date' : undefined,
    query.search ? 'search' : undefined,
  ].filter((item): item is string => item !== undefined);
  return {
    enabled: operators.length > 0 || query.sort === true,
    filterable: operators.some((item) => item !== 'search'),
    searchable: query.search !== undefined,
    sortable: query.sort === true,
    operators,
  };
}

function inlineUse(
  schema: CompiledInlineSchema,
  requiredValue = true,
  nullable = false,
): CompiledSchemaUse {
  return {
    kind: 'inline',
    schema,
    required: requiredValue,
    nullable,
  };
}

function validateOperations(
  operations: readonly CompiledOperation[],
  diagnostics: Diagnostic[],
): void {
  const ids = new Set<string>();
  for (const operation of operations) {
    if (ids.has(operation.operationId)) {
      diagnostics.push(diagnostic(
        'AUTHORING_DUPLICATE_OPERATION_ID',
        'error',
        `Duplicate operation ID: ${operation.operationId}.`,
      ));
    }
    ids.add(operation.operationId);
  }
  for (const operation of operations) {
    for (const target of operation.cacheInvalidates) {
      if (!ids.has(target)) {
        diagnostics.push(diagnostic(
          'AUTHORING_UNKNOWN_CACHE_OPERATION',
          'error',
          `Operation ${operation.operationId} invalidates unknown operation ${target}.`,
        ));
      }
    }
  }
}

function diagnostic(
  code: string,
  severity: Diagnostic['severity'],
  message: string,
): Diagnostic {
  return { code, severity, layer: 'authoring', message };
}

function docsProperty(value: unknown): { readonly docs?: CompiledDocumentation } {
  const compiled = docs(value);
  return compiled ? { docs: compiled } : {};
}

function docs(value: unknown): CompiledDocumentation | undefined {
  if (!dynamicObject(value)) return undefined;
  const summary = typeof value.summary === 'string' ? value.summary : undefined;
  const description = typeof value.description === 'string'
    ? value.description
    : undefined;
  return summary || description
    ? {
        ...(summary ? { summary } : {}),
        ...(description ? { description } : {}),
      }
    : undefined;
}

function owner(value: unknown): string {
  if (!dynamicObject(value)) return 'global';
  if (value.global === true) return 'global';
  const resource = dynamicObject(value.resource) ? value.resource : undefined;
  return resource && typeof resource.name === 'string'
    ? resource.name
    : 'global';
}

function accessRef(value: unknown): string | undefined {
  return dynamicObject(value)
    && typeof value.key === 'string'
    && value.owner !== undefined
    ? `access:${owner(value.owner)}:${value.key}`
    : undefined;
}

function required(value: unknown): boolean {
  if (isRefUsage(value)) return value.usage.required ?? true;
  return dynamicObject(value) && typeof value.required === 'boolean'
    ? value.required
    : true;
}

function bodySchema(value: unknown): unknown {
  return dynamicObject(value) && value.schema !== undefined ? value.schema : value;
}

function responseSchema(value: unknown): unknown {
  return dynamicObject(value) && value.schema !== undefined ? value.schema : value;
}

function noContent(value: unknown): boolean {
  const schema = responseSchema(value);
  return isSchemaField(schema) && schema.kind === SchemaKind.noContent;
}

function joinPath(base: string, path: string): string {
  const left = base === '/' ? '' : base.replace(/\/$/, '');
  const right = path === '/' ? '' : path.replace(/^\//, '');
  return `${left}/${right}`.replace(/\/+/g, '/') || '/';
}

function cardinality(
  value: string,
): 'oneToOne' | 'oneToMany' | 'manyToOne' | 'manyToMany' {
  if (value === 'belongsTo') return 'manyToOne';
  if (value === 'hasMany') return 'oneToMany';
  if (value === 'manyToMany') return 'manyToMany';
  return 'oneToOne';
}

function deleteBehavior(value: unknown): string | undefined {
  if (!dynamicObject(value)) return undefined;
  return Object.keys(value).find((key) => value[key] === true);
}

function refId(value: unknown): string {
  if (isRefUsage(value)) return value.ref.id;
  return isEngineRef(value) ? value.id : 'unknown';
}

function isRef(value: unknown): boolean {
  return isRefUsage(value) || isEngineRef(value);
}

function isEngineRef(value: unknown): value is EngineRef {
  return dynamicObject(value)
    && typeof value.id === 'string'
    && typeof value.name === 'string'
    && Object.values(RefKind).includes(value.kind as never);
}

function isSchemaField(value: unknown): value is SchemaField {
  return dynamicObject(value)
    && typeof value.kind === 'string'
    && Object.values(SchemaKind).includes(value.kind as never);
}

function isProjection(value: unknown): value is {
  readonly source: string;
  readonly sourceRefId: string;
  readonly mode: string;
  readonly fields?: readonly string[];
  readonly steps?: readonly unknown[];
} {
  return dynamicObject(value)
    && value.kind === 'schema-projection-definition'
    && typeof value.source === 'string'
    && typeof value.sourceRefId === 'string'
    && typeof value.mode === 'string';
}

function isZod(value: unknown): value is DynamicObject {
  return dynamicObject(value)
    && (
      value._zod !== undefined
      || value._def !== undefined
      || typeof value.safeParse === 'function'
    );
}

function zodDefinition(value: DynamicObject): DynamicObject {
  const zod = dynamicObject(value._zod) ? value._zod : undefined;
  if (zod && dynamicObject(zod.def)) return zod.def;
  return dynamicObject(value._def) ? value._def : {};
}

function primitive(value: unknown): 'string' | 'number' | 'integer' | 'boolean' | 'bigint' | 'date' | 'null' | 'unknown' {
  if (value === null) return 'null';
  if (typeof value === 'string') return 'string';
  if (typeof value === 'number') return Number.isInteger(value) ? 'integer' : 'number';
  if (typeof value === 'boolean') return 'boolean';
  if (typeof value === 'bigint') return 'bigint';
  if (value instanceof Date) return 'date';
  return 'unknown';
}

function jsonObject(value: unknown): JsonObject {
  const result = jsonValue(value);
  return dynamicObject(result) ? result as JsonObject : {};
}

function jsonValue(value: unknown): JsonValue {
  if (
    value === null
    || typeof value === 'string'
    || typeof value === 'number'
    || typeof value === 'boolean'
  ) return value;
  if (typeof value === 'bigint') return value.toString();
  if (Array.isArray(value)) return value.map(jsonValue);
  if (value instanceof Date) return value.toISOString();
  if (dynamicObject(value)) {
    return Object.fromEntries(
      Object.entries(value)
        .filter(([, item]) =>
          item !== undefined
          && typeof item !== 'function'
          && typeof item !== 'symbol',
        )
        .map(([key, item]) => [key, jsonValue(item)]),
    );
  }
  return String(value);
}

function dynamicObject(value: unknown): value is DynamicObject {
  return Boolean(value && typeof value === 'object' && !Array.isArray(value));
}
