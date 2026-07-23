import {
  CODEPOT_ARTIFACT_VERSION,
  CODEPOT_PROTOCOL_VERSION,
} from '@/contract/index';
import type {
  CompiledAuthoringArtifact,
  CompiledOperation,
  CompiledRelation,
  CompiledResource,
} from '@/contract/index';
import { CODEPOT_ARTIFACT_PRODUCER } from '@/internal/package-info';
import { createCompilerContext, indexSchemaFields } from './compiler-context';
import type {
  AuthoringCompileInput,
  AuthoringCompileOutput,
  AuthoringCompiler,
  AuthoringCompilerDependencies,
} from './compiler.types';
import { collectSchemas } from './passes/collect-contracts';
import { compileAccess } from './passes/compile-access';
import { compileEntities } from './passes/compile-entities';
import { compileFrontends } from './passes/compile-frontends';
import { compileHooks } from './passes/compile-hooks';
import { compileProperties } from './passes/compile-properties';
import { compileRelation } from './passes/compile-relations';
import { compileResource } from './passes/compile-resources';
import { compileSchemas } from './passes/compile-schemas';
import { jsonObject } from './shared/compiler-values';
import { validateOperations } from './validation/validate-operations';

/** Compiles user builders into the stable, JSON-safe authoring artifact. */
export class DefaultAuthoringCompiler implements AuthoringCompiler {
  readonly #dependencies: AuthoringCompilerDependencies;

  constructor(dependencies: AuthoringCompilerDependencies) {
    this.#dependencies = dependencies;
  }

  async compile(input: AuthoringCompileInput): Promise<AuthoringCompileOutput> {
    const context = createCompilerContext(input.config);
    if (context.contracts.length === 0) {
      context.diagnostics.push({
        code: 'AUTHORING_NO_CONTRACTS',
        severity: 'error',
        layer: 'authoring',
        message: 'codepotx.config.ts must define at least one contract.',
      });
    }

    const properties = context.contracts.flatMap((contract) =>
      compileProperties(contract.properties),
    );
    const schemas = compileSchemas(collectSchemas(context.contracts));
    indexSchemaFields(context, schemas);

    const entities = context.contracts.flatMap((contract) => [
      ...compileEntities(contract.baseEntityComponents, context.schemaFields),
      ...compileEntities(contract.entityComponents, context.schemaFields),
      ...contract.resources.flatMap((resource) =>
        compileEntities(resource.entityComponents, context.schemaFields),
      ),
    ]);
    const relations: readonly CompiledRelation[] = context.contracts.flatMap((contract) =>
      contract.resources.flatMap((resource) =>
        resource.entityRelationComponents.flatMap((registry) =>
          registry.definitions.map(compileRelation),
        ),
      ),
    );
    const access = context.contracts.flatMap((contract) => [
      ...compileAccess(contract.accessComponents),
      ...contract.resources.flatMap((resource) =>
        compileAccess(resource.accessComponents),
      ),
    ]);
    const hooks = context.contracts.flatMap((contract) =>
      contract.resources.flatMap((resource) =>
        compileHooks(resource.hookComponents),
      ),
    );
    const frontends = compileFrontends(context.contracts);

    const resources: CompiledResource[] = [];
    const operations: CompiledOperation[] = [];
    for (const contract of context.contracts) {
      for (const resource of contract.resources) {
        const compiled = compileResource(resource, contract, context.diagnostics);
        resources.push(compiled.resource);
        operations.push(...compiled.operations);
      }
    }
    validateOperations(operations, context.diagnostics);

    const first = context.contracts[0];
    const body: Omit<CompiledAuthoringArtifact, 'header'> = {
      source: input.source,
      project: {
        name: first?.info.title ?? 'Codepot',
        version: first?.info.version ?? '0.0.0',
        ...(first?.info.description ? { description: first.info.description } : {}),
        ...(first?.info.license ? { license: jsonObject(first.info.license) } : {}),
        tags: [...new Set(context.contracts.flatMap((contract) => contract.tags))],
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
        contractCount: context.contracts.length,
        ...(input.includeDebugMetadata ? { debug: true } : {}),
      },
      diagnostics: context.diagnostics,
    };
    const contentDigest = await this.#dependencies.hash.text(JSON.stringify(body));
    const artifact: CompiledAuthoringArtifact = {
      header: {
        kind: 'codepot.authoring',
        protocolVersion: CODEPOT_PROTOCOL_VERSION,
        artifactVersion: CODEPOT_ARTIFACT_VERSION,
        producer: CODEPOT_ARTIFACT_PRODUCER,
        contentDigest,
        sourceDigest: input.source.digest,
      },
      ...body,
    };

    return { artifact, diagnostics: context.diagnostics };
  }
}
