import type {
  CompiledAuthoringArtifact,
  CompiledNamedItem,
  CompiledOperation,
  CompiledResource,
  CompiledSchema,
  JsonObject,
  JsonValue,
  TemplateContextRequest,
} from '@/contract/index';

/** Stable naming variants borrowed from the useful Python NameSet contract. */
export interface TemplateNameSet extends JsonObject {
  readonly original: string;
  readonly raw: string;
  readonly camel: string;
  readonly pascal: string;
  readonly snake: string;
  readonly kebab: string;
  readonly constant: string;
  readonly title: string;
  readonly path: string;
}

/**
 * Build the complete JSON-only context templates receive. Raw authoring remains
 * available under `authoring` and `api`, while classified views avoid repeated
 * filtering and naming logic inside every template pack.
 */
export function buildTemplateContext(request: TemplateContextRequest): JsonObject {
  const authoring = request.authoring;
  const schemas = authoring.schemas.map(enrichSchema);
  const classified = classifySchemas(schemas);
  const operations = authoring.operations.map((item) => enrichOperation(item, authoring));
  const resources = authoring.resources.map((item) => enrichResource(item, authoring));
  const entities = authoring.entities.map(enrichNamedItem);
  const frontends = authoring.frontends.map(enrichNamedItem);
  const selected = request.selectedFrontend
    ? frontends.find((item) => readOriginalName(item) === request.selectedFrontend)
    : undefined;

  const project: JsonObject = {
    ...authoring.project,
    ...request.project,
    name: createNameSet(authoring.project.name),
    docs: {
      summary: authoring.project.name,
      description: authoring.project.description ?? '-',
      deprecated: false,
      examples: [],
    },
  };
  const dependencies: readonly JsonObject[] = [];
  const imports: readonly JsonObject[] = [];

  return {
    project,
    api: authoring as unknown as JsonObject,
    authoring: authoring as unknown as JsonObject,
    resources,
    features: resources,
    schemas: classified,
    operations,
    entities,
    frontends,
    variables: request.variables ?? {},
    language: request.language ?? {},
    lang: request.language ?? {},
    emit: request.emit ?? generationEmitPlaceholder(),
    file: request.file ?? generationFilePlaceholder(),
    dependencies,
    imports,
    frontendCount: frontends.length,
    frontend_count: frontends.length,
    meta: {
      schemaCount: schemas.length,
      modelCount: classified.models.length,
      dtoCount: classified.dtos.length,
      enumCount: classified.enums.length,
      primitiveCount: classified.primitives.length,
      operationCount: operations.length,
      resourceCount: resources.length,
      entityCount: entities.length,
      frontendCount: frontends.length,
    },
    ...(selected ? {
      frontend: selected,
      selectedFrontend: selected,
      selected_frontend: selected,
      selectedFrontends: [selected],
      selected_frontends: [selected],
    } : {
      selectedFrontends: [],
      selected_frontends: [],
    }),
  };
}

export function createNameSet(value: string): TemplateNameSet {
  const words = splitWords(value);
  const snake = words.map((word) => word.toLowerCase()).join('_');
  const pascal = words.map(capitalize).join('');
  return {
    original: value,
    raw: value,
    camel: pascal ? pascal[0]!.toLowerCase() + pascal.slice(1) : '',
    pascal,
    snake,
    kebab: words.map((word) => word.toLowerCase()).join('-'),
    constant: snake.toUpperCase(),
    title: words.map(capitalize).join(' '),
    path: snake,
  };
}

function enrichNamedItem<T extends CompiledNamedItem>(item: T): JsonObject {
  const docs: JsonObject = item.docs
    ? {
        ...(item.docs.summary ? { summary: item.docs.summary } : {}),
        ...(item.docs.description ? { description: item.docs.description } : {}),
        ...(item.docs.deprecated === undefined ? {} : { deprecated: item.docs.deprecated }),
        ...(item.docs.examples ? { examples: item.docs.examples } : {}),
      }
    : { summary: item.name, description: '-', deprecated: false, examples: [] };
  return {
    ...(item as unknown as JsonObject),
    key: item.key,
    name: createNameSet(item.name),
    docs,
    emit: generationEmitPlaceholder(item.id),
  };
}

function enrichSchema(schema: CompiledSchema): JsonObject {
  const fields = schema.schema.kind === 'object'
    ? schema.schema.fields.map((field) => ({
        ...enrichNamedItem(field),
        wireName: field.wireName,
        lang: {
          required: field.schema.required,
          nullable: field.schema.nullable,
          selectable: field.lifecycle.selectable,
          editable: field.lifecycle.editable,
          immutable: field.lifecycle.immutable,
          managed: field.lifecycle.managed,
          queryEnabled: field.query.enabled,
          filterable: field.query.filterable,
          searchable: field.query.searchable,
          sortable: field.query.sortable,
          operators: field.query.operators,
        },
      }))
    : [];
  const refs = collectReferences(schema.schema as unknown as JsonValue);
  return {
    ...enrichNamedItem(schema),
    fields,
    lang: {
      kind: schema.schema.kind,
      fieldCount: fields.length,
      dependencyCount: refs.length,
      queryEnabled: fields.some((field) => Boolean((field.lang as JsonObject).queryEnabled)),
    },
    meta: {
      ...(schema.metadata ?? {}),
      role: schema.role ?? null,
      entityRef: schema.entityRef ?? null,
      dependencyRefs: refs,
    },
    emit: {
      ...generationEmitPlaceholder(schema.id),
      dependencyRefs: refs,
      dependency_refs: refs,
    },
  };
}

function enrichResource(resource: CompiledResource, authoring: CompiledAuthoringArtifact): JsonObject {
  const operations = authoring.operations
    .filter((item) => item.resourceId === resource.id)
    .map((item) => enrichOperation(item, authoring));
  return {
    ...enrichNamedItem(resource),
    path: resource.folders,
    operations,
    models: [],
    dtos: [],
    enums: [],
    schemas: [],
    entities: authoring.entities
      .filter((item) => item.owner === resource.id || item.owner === resource.name)
      .map(enrichNamedItem),
    lang: { kind: 'resource', displayName: resource.name },
    meta: {
      ...(resource.metadata ?? {}),
      operationsCount: operations.length,
      route: resource.route,
      tags: resource.tags,
      accessRef: resource.accessRef ?? null,
      frontend: resource.frontend ?? {},
    },
  };
}

function enrichOperation(operation: CompiledOperation, authoring: CompiledAuthoringArtifact): JsonObject {
  const resource = authoring.resources.find((item) => item.id === operation.resourceId);
  const operationName = createNameSet(operation.operationId);
  return {
    ...enrichNamedItem(operation),
    parameters: operation.parameters.map(enrichNamedItem),
    requestBody: operation.requestBody ? enrichNamedItem(operation.requestBody) : null,
    request_body: operation.requestBody ? enrichNamedItem(operation.requestBody) : null,
    responses: operation.responses.map(enrichNamedItem),
    resource: resource ? {
      id: resource.id,
      name: createNameSet(resource.name),
      path: resource.folders,
      route: resource.route,
    } : null,
    lang: {
      kind: 'operation',
      functionName: operationName.camel,
      displayName: operationName.title,
      method: operation.method,
      endpointPath: operation.path,
    },
    meta: {
      ...(operation.metadata ?? {}),
      parameterCount: operation.parameters.length,
      responseCount: operation.responses.length,
      hasRequestBody: Boolean(operation.requestBody),
      tags: operation.tags,
      cacheInvalidates: operation.cacheInvalidates,
      accessRef: operation.accessRef ?? null,
      hookRefs: operation.hookRefs,
      effects: operation.effects,
    },
  };
}

interface ClassifiedSchemas extends JsonObject {
  readonly all: readonly JsonObject[];
  readonly models: readonly JsonObject[];
  readonly dtos: readonly JsonObject[];
  readonly enums: readonly JsonObject[];
  readonly primitives: readonly JsonObject[];
}

function classifySchemas(all: readonly JsonObject[]): ClassifiedSchemas {
  const models = all.filter((item) => schemaRole(item) === 'model');
  const dtos = all.filter((item) => schemaRole(item) === 'dto');
  const enums = all.filter((item) => schemaKind(item) === 'enum');
  const primitives = all.filter((item) => schemaKind(item) === 'primitive');
  const aliases = all.filter((item) => Boolean((item.meta as JsonObject | undefined)?.aliasOf));
  const queries = all.filter((item) => schemaRole(item) === 'query');
  const params = all.filter((item) => schemaRole(item) === 'params');
  const bodies = all.filter((item) => schemaRole(item) === 'body');
  const responses = all.filter((item) => schemaRole(item) === 'response');
  const known = new Set([...models, ...dtos, ...enums, ...primitives, ...aliases]);
  return {
    all,
    models,
    dtos,
    enums,
    primitives,
    aliases,
    unknown: all.filter((item) => !known.has(item)),
    queries,
    params,
    bodies,
    responses,
    emitModels: models,
    emitDtos: dtos,
    emitEnums: enums,
    emit_models: models,
    emit_dtos: dtos,
    emit_enums: enums,
  };
}

function generationEmitPlaceholder(ref: string | null = null): JsonObject {
  return {
    group: '',
    path: '',
    fileName: '',
    file_name: '',
    folderPath: '',
    folder_path: '',
    resourcePath: '',
    resource_path: '',
    ref,
    dependencyRefs: [],
    dependency_refs: [],
    dependencies: [],
    imports: [],
  };
}

function generationFilePlaceholder(): JsonObject {
  return {
    templateId: '',
    group: '',
    path: '',
    outputPath: '',
    directory: '',
    name: '',
    stem: '',
    extension: '',
    depth: 0,
    rootPrefix: './',
    subjectRefs: [],
    dependencies: [],
    imports: [],
  };
}

function schemaRole(item: JsonObject): string | undefined {
  if (typeof item.role === 'string') return item.role;
  const meta = item.meta as JsonObject | undefined;
  return typeof meta?.role === 'string' ? meta.role : undefined;
}

function schemaKind(item: JsonObject): string | undefined {
  const value = item.schema;
  if (!value || typeof value !== 'object' || Array.isArray(value)) return undefined;
  const object = value as JsonObject;
  return typeof object.kind === 'string' ? object.kind : undefined;
}

function collectReferences(value: JsonValue): readonly string[] {
  const output = new Set<string>();
  const visit = (current: JsonValue): void => {
    if (Array.isArray(current)) {
      for (const item of current) visit(item);
      return;
    }
    if (!current || typeof current !== 'object') return;
    const object = current as JsonObject;
    if (object.kind === 'ref' && typeof object.ref === 'string') output.add(object.ref);
    for (const nested of Object.values(object)) visit(nested);
  };
  visit(value);
  return [...output].sort();
}

function readOriginalName(item: JsonObject): string | undefined {
  const name = item.name;
  if (!name || typeof name !== 'object' || Array.isArray(name)) return undefined;
  return typeof name.original === 'string' ? name.original : undefined;
}

function splitWords(value: string): string[] {
  return value.replace(/([a-z0-9])([A-Z])/g, '$1 $2').split(/[^A-Za-z0-9]+/).filter(Boolean);
}

function capitalize(value: string): string {
  return value ? value[0]!.toUpperCase() + value.slice(1).toLowerCase() : value;
}
