import type { VersionContract } from '../version/version-contract.types.js';
import type { CompilerContext, ResolvedCompilerContext } from './compiler-context.js';
import { resolveCompilerContext } from './compiler-context.js';
import { OpenApiVersion } from '../openapi/openapi-version.js';
import type { OpenApiDocument } from '../openapi/openapi.types.js';
import { validateContract } from '../validation/validate-contract.js';
import { compileComponents } from './compile-components.js';
import { compilePaths } from './paths/compile-paths.js';
import type { CompileOptions } from './compile-options.types.js';
import type { CompileResult } from './compile-result.types.js';
import { compileInferredComponents } from './paths/compile-inferred-components.js';
import { resolvePendingRefs } from './refs/resolve-pending-refs.js';
import { collectDtoRoleUsageFromContract } from './dto-role-usage.js';
import { collectAccessMetadataFromContract } from './access-metadata.js';
import { compileEntityMetadata } from './entity-metadata.js';
import type { RefResolver } from './refs/ref-resolver.types.js';
import { compileAccessRegistryMetadata } from './access-registry-metadata.js';
import { compileFrontendMetadata } from './frontend-metadata.js';

export function compileOpenApi(contract: VersionContract, options: CompileOptions = {}, context: CompilerContext = {}): CompileResult {
  const resolvedContext = resolveCompilerContext(context);
  const shouldValidate = options.validate ?? true;
  const validation = shouldValidate ? validateContract(contract) : { valid: true, issues: [] };

  const document = createOpenApiShell(contract, options, resolvedContext);

  if (!validation.valid) {
    return {
      success: false,
      document,
      issues: validation.issues,
    };
  }

  return {
    success: true,
    document,
    issues: [],
  };
}

function createOpenApiShell(contract: VersionContract, options: CompileOptions, context: ResolvedCompilerContext): OpenApiDocument {
  // Prepass: collect DTO role usage from routes
  collectAccessMetadataFromContract(contract, context);
  collectDtoRoleUsageFromContract(contract, context);

  // Compile components first
  const compiledComponents = compileComponents(contract, context);

  // Compile paths using the resolver from components
  const { paths, inferredComponents } = compilePaths(contract, compiledComponents.resolver, context);
  const compiledInferred = compileInferredComponents(inferredComponents, compiledComponents.resolver, context);

  const document = {
    openapi: options.openapi ?? OpenApiVersion.v3_1_0,
    info: {
      title: contract.info.title,
      version: contract.info.version,
      description: contract.info.description,
      license: contract.info.license,
    },
    servers: options.servers ? [...options.servers] : undefined,
    security: [{ bearerAuth: [] }],
    paths,
    components: {
      ...compiledComponents.components,
      parameters: {
        ...compiledInferred.parameters,
        ...compiledComponents.components.parameters,
      },
      requestBodies: {
        ...compiledInferred.requestBodies,
        ...compiledComponents.components.requestBodies,
      },
      responses: {
        ...compiledInferred.responses,
        ...compiledComponents.components.responses,
      },
      securitySchemes: {
        bearerAuth: {
          type: 'http',
          scheme: 'bearer',
          bearerFormat: 'JWT',
        },
      },
    },
    'x-codegen': createDocumentCodegenMetadata(contract, compiledComponents.resolver),
  };

  return resolvePendingRefs(document, compiledComponents.resolver, context) as OpenApiDocument;
}

function createDocumentCodegenMetadata(contract: VersionContract, resolver: RefResolver): Record<string, unknown> | undefined {
  const entities = compileEntityMetadata(contract, resolver);
  const accessRegistry = compileAccessRegistryMetadata(contract, resolver);
  const resources = compileResourceRegistry(contract, accessRegistry.resourceAccess);
  const frontends = compileFrontendMetadata(contract, resolver);
  const metadata = cleanObject({
    resources,
    frontends,
    access: accessRegistry.access,
    ...entities,
  });

  return Object.keys(metadata).length > 0 ? metadata : undefined;
}

function compileResourceRegistry(
  contract: VersionContract,
  resourceAccess: Record<string, Record<string, unknown>>,
): Record<string, unknown> | undefined {
  const resources: Record<string, unknown> = {};

  for (const resource of contract.resources) {
    const key = resource.context.alias;

    if (resources[key]) {
      throw new Error(`Duplicate x-codegen resource key "${key}". Resource names must be unique before refs can be emitted.`);
    }

    const hooks = Object.fromEntries(
      resource.hookComponents.flatMap((registry) =>
        registry.definitions.map((definition) => [
          definition.key,
          cleanObject({
            phase: definition.phase,
            transport: definition.transport,
            description: definition.description,
          }),
        ]),
      ),
    );

    resources[key] = cleanObject({
      name: resource.context.alias,
      path: resource.context.folders,
      route: resource.context.route,
      tags: resource.context.tags,
      ui: resource.context.ui,
      info: resource.context.info,
      hooks: Object.keys(hooks).length > 0 ? hooks : undefined,
      access: resourceAccess[key] && Object.keys(resourceAccess[key]).length > 0 ? resourceAccess[key] : undefined,
    });
  }

  return Object.keys(resources).length > 0 ? resources : undefined;
}

function cleanObject(input: Record<string, unknown>): Record<string, unknown> {
  return Object.fromEntries(Object.entries(input).filter(([, value]) => value !== undefined));
}
