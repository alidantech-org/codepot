import {
  CODEPOT_ARTIFACT_VERSION,
  CODEPOT_PROTOCOL_VERSION,
} from '@/contract/index';
import type {
  CompiledAccessDefinition,
  CompiledAuthoringArtifact,
  CompiledEntity,
  CompiledEntityConstraint,
  CompiledField,
  CompiledFrontend,
  CompiledHook,
  CompiledInlineSchema,
  CompiledMediaTypeSchema,
  CompiledOperation,
  CompiledParameter,
  CompiledPrimitiveKind,
  CompiledPropertyGroup,
  CompiledRequestBody,
  CompiledResource,
  CompiledResponse,
  CompiledSchema,
  CompiledSchemaConstraint,
  CompiledSchemaUse,
  Diagnostic,
  JsonObject,
  JsonValue,
} from '@/contract/index';
import type { AccessRegistry } from '../access/access.types';
import type { SchemaComponentDefinition, SchemaComponentRegistry } from '../components/component.types';
import type { EntityDefinition, EntityRegistry } from '../entities/entity.types';
import type { RuntimeHookRegistry } from '../hooks/hooks.types';
import type { PropertyDefinition, PropertyRegistry } from '../properties/property.types';
import { isRefUsage } from '../refs/ref-methods';
import { RefKind } from '../refs/ref-kind';
import type { EngineRef, RequestBodyRef, ResponseRef } from '../refs/ref.types';
import type { RefUsage } from '../refs/ref-usage.types';
import type { ResourceBuilder } from '../resource/resource.types';
import type { RouteBodyInput, RouteDefinition, RouteQueryInput, RouteResponseInput } from '../routes/route.types';
import { SchemaKind } from '../schema/schema-kind';
import type { SchemaField } from '../schema/schema.types';
import type { VersionBuilder, VersionContract } from '../version/version.types';
import type { AuthoringCompileInput, AuthoringCompileOutput, AuthoringCompiler, AuthoringCompilerDependencies } from './compiler.types';

export class DefaultAuthoringCompiler implements AuthoringCompiler {
  readonly #dependencies: AuthoringCompilerDependencies;
  constructor(dependencies: AuthoringCompilerDependencies) { this.#dependencies = dependencies; }
  async compile(input: AuthoringCompileInput): Promise<AuthoringCompileOutput> {
    const diagnostics: Diagnostic[] = [];
    const contracts = input.config.contracts.map(toContract);
    if (contracts.length === 0) diagnostics.push(error('AUTHORING_NO_CONTRACTS', 'codepotx.config.ts must define at least one contract.'));
    const properties = contracts.flatMap((contract) => compileProperties(contract.properties));
    const schemaDefinitions = collectSchemaDefinitions(contracts);
    const schemas = compileSchemas(schemaDefinitions);
    const schemaByRef = new Map(schemas.map((schema) => [schema.id, schema]));
    const entities = contracts.flatMap((contract) => [
      ...compileEntities(contract.baseEntityComponents, schemaByRef),
      ...compileEntities(contract.entityComponents, schemaByRef),
      ...contract.resources.flatMap((resource) => compileEntities(resource.entityComponents, schemaByRef)),
    ]);
    const relations = contracts.flatMap((contract) => contract.resources.flatMap((resource) => resource.entityRelationComponents.flatMap((registry) => registry.definitions.map((relation) => ({
      id: `relation:${relation.source}:${relation.name}`,
      key: relation.name,
      name: relation.name,
      sourceEntity: relation.source,
      targetEntity: relation.target.id,
      sourceField: relation.local,
      targetField: relation.foreign,
      cardinality: mapCardinality(relation.cardinality),
      required: relation.onDelete?.setNull !== true,
      ...(relation.onDelete ? { deleteBehavior: Object.keys(relation.onDelete).find((key) => relation.onDelete?.[key as keyof typeof relation.onDelete]) } : {}),
    })))));
    const access = contracts.flatMap((contract) => [
      ...compileAccess(contract.accessComponents),
      ...contract.resources.flatMap((resource) => compileAccess(resource.accessComponents)),
    ]);
    const hooks = contracts.flatMap((contract) => contract.resources.flatMap((resource) => compileHooks(resource.hookComponents)));
    const frontends = contracts.flatMap((contract) => contract.frontends.map((frontend) => ({
      id: `frontend:${frontend.context.name}`,
      key: frontend.context.name,
      name: frontend.context.name,
      components: frontend.components,
      screens: frontend.screens,
      ...(frontend.context.info ? { docs: frontend.context.info } : {}),
      ...(frontend.context.metadata ? { metadata: frontend.context.metadata } : {}),
    } satisfies CompiledFrontend)));
    const resources: CompiledResource[] = [];
    const operations: CompiledOperation[] = [];
    for (const contract of contracts) {
      for (const resource of contract.resources) {
        const compiled = compileResource(resource, contract, diagnostics);
        resources.push(compiled.resource);
        operations.push(...compiled.operations);
      }
    }
    validateOperationIds(operations, diagnostics);
    validateCacheInvalidations(operations, diagnostics);
    const projectContract = contracts[0];
    const project = {
      name: projectContract?.info.title ?? 'Codepot',
      version: projectContract?.info.version ?? '0.0.0',
      ...(projectContract?.info.description ? { description: projectContract.info.description } : {}),
      ...(projectContract?.info.license ? { license: toJsonObject(projectContract.info.license) } : {}),
      tags: [...new Set(contracts.flatMap((contract) => contract.tags))],
      defaults: toJsonObject(projectContract?.defaults ?? {}),
      ...(input.config.metadata ? { metadata: input.config.metadata } : {}),
    };
    const body = {
      source: input.source,
      project,
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

function toContract(value: VersionBuilder | VersionContract): VersionContract { return 'contract' in value ? value.contract : value; }
function collectSchemaDefinitions(contracts: readonly VersionContract[]): Array<{ readonly group: string; readonly definition: SchemaComponentDefinition; readonly refId: string }> {
  const output: Array<{ readonly group: string; readonly definition: SchemaComponentDefinition; readonly refId: string }> = [];
  const pushRegistry = (registry: SchemaComponentRegistry): void => { for (const definition of registry.definitions) { const ref = registry.ref[definition.name]; output.push({ group: registry.name, definition, refId: ref?.id ?? `component:schema:${definition.name}` }); } };
  for (const contract of contracts) {
    contract.schemaComponents.forEach(pushRegistry);
    for (const resource of contract.resources) resource.schemaComponents.forEach(pushRegistry);
  }
  return output;
}
function compileProperties(registries: readonly PropertyRegistry[]): CompiledPropertyGroup[] {
  return registries.flatMap((registry) => registry.definitions.map((definition) => ({ id: ²È="24ÁÉ¥µ¥Ñ¥Ù”œ°ÁÉ¥µ¥Ñ¥Ù”è€Õ¹­¹½Ý¸œ°½¹ÍÑÉ…¥¹ÑÌèmtôì)ô)™Õ¹Ñ¥½¸½µÁ¥±•i½¡Í¡•µ„èÕ¹­¹½Ý¸¤è½µÁ¥±•‘%¹±¥¹•M¡•µ„ì(€½¹ÍÐ‘•˜€ôé½‘•˜¡Í¡•µ„¤ì(€½¹ÍÐÑåÁ”€ôMÑÉ¥¹œ¡‘•˜ü¹ÑåÁ”€üü€Õ¹­¹½Ý¸œ¤ì(€¥˜€¡ÑåÁ”€ôôô€½ÁÑ¥½¹…°œñðÑåÁ”€ôôô€¹Õ±±…‰±”œñðÑåÁ”€ôôô€‘•™…Õ±ÐœñðÑåÁ”€ôôô€É•…‘½¹±äœñðÑåÁ”€ôôô€…Ñ œ¤É•ÑÕÉ¸½µÁ¥±•i½¡‘•˜ü¹¥¹¹•ÉQåÁ”¤ì(€¥˜€¡ÑåÁ”€ôôô€…ÉÉ…äœ¤É•ÑÕÉ¸ì­¥¹è€…ÉÉ…äœ°¥Ñ•µÌè½µÁ¥±•UÍ”¡‘•˜ü¹•±•µ•¹Ð¤°½¹ÍÑÉ…¥¹ÑÌè½µÁ¥±•¡•­Ì¡‘•˜¤ôì(€¥˜€¡ÑåÁ”€ôôô€½‰©•Ðœ¤ì½¹ÍÐÍ¡…Á”€ôÑåÁ•½˜‘•˜ü¹Í¡…Á”€ôôô€™Õ¹Ñ¥½¸œ€ü‘•˜¹Í¡…Á” ¤€è‘•˜ü¹Í¡…Á”€üüíôìÉ•ÑÕÉ¸ì­¥¹è€½‰©•Ðœ°™¥•±‘Ìè=‰©•Ð¹•¹ÑÉ¥•Ì¡Í¡…Á”…ÌI•½ÉñÍÑÉ¥¹œ°Õ¹­¹½Ý¸ø¤¹µ…À ¡m­•ä°™¥•±‘t¤€ôø½µÁ¥±•¥•±¡™¥•±è‘í­•åõ€°­•ä°™¥•±¤¤°•áÑ•¹‘Ìèmt°…‘‘¥Ñ¥½¹…±AÉ½Á•ÉÑ¥•Ìè™…±Í”ôìô(€¥˜€¡ÑåÁ”€ôôô€ÑÕÁ±”œ¤É•ÑÕÉ¸ì­¥¹è€ÑÕÁ±”œ°¥Ñ•µÌè€¡‘•˜ü¹¥Ñ•µÌ…ÌÕ¹­¹½Ý¹mt€üümt¤¹µ…À¡½µÁ¥±•UÍ”¤ôì(€¥˜€¡ÑåÁ”€ôôô€Õ¹¥½¸œ¤É•ÑÕÉ¸ì­¥¹è€Õ¹¥½¸œ°µ½‘”è€Õ¹¥½¸œ°Ù…É¥…¹ÑÌè€¡‘•˜ü¹½ÁÑ¥½¹Ì…ÌÕ¹­¹½Ý¹mt€üümt¤¹µ…À¡½µÁ¥±•UÍ”¤ôì(€¥˜€¡ÑåÁ”€ôôô€¥¹Ñ•ÉÍ•Ñ¥½¸œ¤É•ÑÕÉ¸ì­¥¹è€Õ¹¥½¸œ°µ½‘”è€…±±=˜œ…Ì€Õ¹¥½¸œ°Ù…É¥…¹ÑÌèm½µÁ¥±•UÍ”¡‘•˜ü¹±•™Ð¤°½µÁ¥±•UÍ”¡‘•˜ü¹É¥¡Ð¥tôì(€¥˜€¡ÑåÁ”€ôôô€É•½Éœ¤É•ÑÕÉ¸ì­¥¹è€É•½Éœ°€¸¸¸¡‘•˜ü¹­•åQåÁ”€üì­•åÌè½µÁ¥±•UÍ”¡‘•˜¹­•åQåÁ”¤ô€èíô¤°Ù…±Õ•Ìè½µÁ¥±•UÍ”¡‘•˜ü¹Ù…±Õ•QåÁ”¤ôì(€¥˜€¡ÑåÁ”€ôôô€±¥Ñ•É…°œ¤ì½¹ÍÐÙ…±Õ•Ì€ô€¡‘•˜ü¹Ù…±Õ•Ì…ÌÕ¹­¹½Ý¹mtðÕ¹‘•™¥¹•¤€üüm‘•˜ü¹Ù…±Õ•tìÉ•ÑÕÉ¸Ù…±Õ•Ì¹±•¹Ñ €ôôô€Ä€üì­¥¹è€±¥Ñ•É…°œ°Ù…±Õ”èÑ½)Í½¹Y…±Õ”¡Ù…±Õ•ÍlÁt¤ô€èì­¥¹è€•¹Õ´œ°Ù…±Õ•QåÁ”èÑåÁ•½˜Ù…±Õ•ÍlÁt€ôôô€¹Õµ‰•Èœ€ü€¹Õµ‰•Èœ€è€ÍÑÉ¥¹œœ°½ÁÑ¥½¹ÌèÙ…±Õ•Ì¹µ…À ¡¥Ñ•´¤€ôø€¡ì­•äèMÑÉ¥¹œ¡¥Ñ•´¤°Ù…±Õ”èÑåÁ•½˜¥Ñ•´€ôôô€¹Õµ‰•Èœ€ü¥Ñ•´€èMÑÉ¥¹œ¡¥Ñ•´¤ô¤¤ôìô(€¥˜€¡ÑåÁ”€ôôô€•¹Õ´œ¤ì½¹ÍÐ•¹ÑÉ¥•Ì€ô‘•˜ü¹•¹ÑÉ¥•Ì…ÌI•½ÉñÍÑÉ¥¹œ°ÍÑÉ¥¹œð¹Õµ‰•ÈøðÕ¹‘•™¥¹•ì½¹ÍÐÙ…±Õ•Ì€ô•¹ÑÉ¥•Ì€ül¸¸¹¹•ÜM•Ð¡=‰©•Ð¹Ù…±Õ•Ì¡•¹ÑÉ¥•Ì¤¥t€èmtìÉ•ÑÕÉ¸ì­¥¹è€•¹Õ´œ°Ù…±Õ•QåÁ”èÑåÁ•½˜Ù…±Õ•ÍlÁt€ôôô€¹Õµ‰•Èœ€ü€¹Õµ‰•Èœ€è€ÍÑÉ¥¹œœ°½ÁÑ¥½¹ÌèÙ…±Õ•Ì¹µ…À ¡¥Ñ•´¤€ôø€¡ì­•äèMÑÉ¥¹œ¡¥Ñ•´¤°Ù…±Õ”è¥Ñ•´ô¤¤ôìô(€½¹ÍÐÁÉ¥µ¥Ñ¥Ù”€ôÁÉ¥µ¥Ñ¥Ù•½È¡ÑåÁ”°½µÁ¥±•¡•­Ì¡‘•˜¤¤ì(€É•ÑÕÉ¸ì­¥¹è€ÁÉ¥µ¥Ñ¥Ù”œ°ÁÉ¥µ¥Ñ¥Ù”èÁÉ¥µ¥Ñ¥Ù”¹­¥¹°€¸¸¸¡ÁÉ¥µ¥Ñ¥Ù”¹™½Éµ…Ð€üì™½Éµ…ÐèÁÉ¥µ¥Ñ¥Ù”¹™½Éµ…Ðô€èíô¤°½¹ÍÑÉ…¥¹ÑÌè½µÁ¥±•¡•­Ì¡‘•˜¤ôì)ô)™Õ¹Ñ¥½¸ÁÉ¥µ¥Ñ¥Ù•½È¡ÑåÁ”èÍÑÉ¥¹œ°¡•­ÌèÉ•…‘½¹±ä½µÁ¥±•‘M¡•µ…½¹ÍÑÉ…¥¹Ñmt¤èìÉ•…‘½¹±ä­¥¹è½µÁ¥±•‘AÉ¥µ¥Ñ¥Ù•-¥¹ìÉ•…‘½¹±ä™½Éµ…ÐüèÍÑÉ¥¹œôì¥˜€¡ÑåÁ”€ôôô€ÍÑÉ¥¹œœ¤ì½¹ÍÐ™½Éµ…Ð€ô¡•­Ì¹™¥¹ ¡¡•¬¤€ôø¡•¬¹­¥¹€ôôô€ÍÑÉ¥¹}™½Éµ…Ðœ¤ü¹µ•Ñ…‘…Ñ„ü¹™½Éµ…ÐìÉ•ÑÕÉ¸ì­¥¹è€ÍÑÉ¥¹œœ°€¸¸¸¡ÑåÁ•½˜™½Éµ…Ð€ôôô€ÍÑÉ¥¹œœ€üì™½Éµ…Ðô€èíô¤ôìô¥˜€¡ÑåÁ”€ôôô€¹Õµ‰•Èœ¤É•ÑÕÉ¸ì­¥¹è¡•­Ì¹Í½µ” ¡¡•¬¤€ôø¡•¬¹­¥¹€ôôô€¥¹Ñ••Èœ¤€ü€¥¹Ñ••Èœ€è€¹Õµ‰•Èœôì¥˜€¡ÑåÁ”€ôôô€‰½½±•…¸œ¤É•ÑÕÉ¸ì­¥¹è€‰½½±•…¸œôì¥˜€¡ÑåÁ”€ôôô€‰¥¥¹Ðœ¤É•ÑÕÉ¸ì­¥¹è€‰¥¥¹Ðœôì¥˜€¡ÑåÁ”€ôôô€‘…Ñ”œ¤É•ÑÕÉ¸ì­¥¹è€‘…Ñ”œôì¥˜€¡ÑåÁ”€ôôô€¹Õ±°œ¤É•ÑÕÉ¸ì­¥¹è€¹Õ±°œôìÉ•ÑÕÉ¸ì­¥¹è€Õ¹­¹½Ý¸œôìô)™Õ¹Ñ¥½¸½µÁ¥±•¡•­Ì¡‘•˜èI•½ÉñÍÑÉ¥¹œ°Õ¹­¹½Ý¸øðÕ¹‘•™¥¹•¤è½µÁ¥±•‘M¡•µ…½¹ÍÑÉ…¥¹ÑmtìÉ•ÑÕÉ¸€ ¡‘•˜ü¹¡•­Ì…ÌÕ¹­¹½Ý¹mtðÕ¹‘•™¥¹•¤€üümt¤¹µ…À ¡¡•¬¤€ôøì½¹ÍÐÙ…±Õ”€ôé½‘•˜¡¡•¬¤€üü¡•¬…ÌI•½ÉñÍÑÉ¥¹œ°Õ¹­¹½Ý¸øì½¹ÍÐ­¥¹€ôMÑÉ¥¹œ¡Ù…±Õ”¹¡•¬€üüÙ…±Õ”¹ÑåÁ”€üü€¡•¬œ¤ì½¹ÍÐµ•Ñ…‘…Ñ„èI•½ÉñÍÑÉ¥¹œ°)Í½¹Y…±Õ”ø€ôíôì™½È€¡½¹ÍÐ­•ä½˜l™½Éµ…Ðœ°€Á…ÑÑ•É¸œ°€µ¥¹¥µÕ´œ°€µ…á¥µÕ´œ°€¥¹±ÕÍ¥Ù”t¤ì½¹ÍÐ¥Ñ•´€ôÙ…±Õ•m­•åtì¥˜€¡ÑåÁ•½˜¥Ñ•´€ôôô€ÍÑÉ¥¹œœñðÑåÁ•½˜¥Ñ•´€ôôô€¹Õµ‰•ÈœñðÑåÁ•½˜¥Ñ•´€ôôô€‰½½±•…¸œñð¥Ñ•´€ôôô¹Õ±°¤µ•Ñ…‘…Ñ…m­•åt€ô¥Ñ•´ìôÉ•ÑÕÉ¸ì­¥¹°€¸¸¸¡Ù…±Õ”¹Ù…±Õ”€„ôôÕ¹‘•™¥¹•€üìÙ…±Õ”èÑ½)Í½¹Y…±Õ”¡Ù…±Õ”¹Ù…±Õ”¤ô€èíô¤°€¸¸¸¡=‰©•Ð¹­•åÌ¡µ•Ñ…‘…Ñ„¤¹±•¹Ñ €üìµ•Ñ…‘…Ñ„èµ•Ñ…‘…Ñ„…Ì)Í½¹=‰©•Ðô€èíô¤ôìô¤ìô)™Õ¹Ñ¥½¸é½‘•˜¡Ù…±Õ”èÕ¹­¹½Ý¸¤èI•½ÉñÍÑÉ¥¹œ°Õ¹­¹½Ý¸øðÕ¹‘•™¥¹•ì¥˜€ …Ù…±Õ”ñðÑåÁ•½˜Ù…±Õ”€„ôô€½‰©•Ðœ¤É•ÑÕÉ¸Õ¹‘•™¥¹•ì½¹ÍÐÍ¡•µ„€ôÙ…±Õ”…ÌìÉ•…‘½¹±ä}é½üèìÉ•…‘½¹±ä‘•˜üèI•½ÉñÍÑÉ¥¹œ°Õ¹­¹½Ý¸øôìÉ•…‘½¹±ä}‘•˜üèI•½ÉñÍÑÉ¥¹œ°Õ¹­¹½Ý¸øôìÉ•ÑÕÉ¸Í¡•µ„¹}é½ü¹‘•˜€üüÍ¡•µ„¹}‘•˜ìô)™Õ¹Ñ¥½¸¥Íi½¡Ù…±Õ”èÕ¹­¹½Ý¸¤è‰½½±•…¸ìÉ•ÑÕÉ¸	½½±•…¸¡é½‘•˜¡Ù…±Õ”¤¤ìô)™Õ¹Ñ¥½¸Í¡•µ…I•ÅÕ¥É•¡Ù…±Õ”èÕ¹­¹½Ý¸¤è‰½½±•…¸ì½¹ÍÐÑåÁ”€ôé½‘•˜¡Ù…±Õ”¤ü¹ÑåÁ”ì¥˜€¡ÑåÁ”€ôôô€½ÁÑ¥½¹…°œ¤É•ÑÕÉ¸™…±Í”ì¥˜€¡Ù…±Õ”€˜˜ÑåÁ•½˜Ù…±Õ”€ôôô€½‰©•Ðœ€˜˜€É•ÅÕ¥É•œ¥¸Ù…±Õ”€˜˜€¡Ù…±Õ”…ÌìÉ•…‘½¹±äÉ•ÅÕ¥É•üè‰½½±•…¸ô¤¹É•ÅÕ¥É•€ôôô™…±Í”¤É•ÑÕÉ¸™…±Í”ìÉ•ÑÕÉ¸ÑÉÕ”ìô)™Õ¹Ñ¥½¸Í¡•µ…9Õ±±…‰±”¡Ù…±Õ”èÕ¹­¹½Ý¸¤è‰½½±•…¸ì½¹ÍÐÑåÁ”€ôé½‘•˜¡Ù…±Õ”¤ü¹ÑåÁ”ì¥˜€¡ÑåÁ”€ôôô€¹Õ±±…‰±”œ¤É•ÑÕÉ¸ÑÉÕ”ì¥˜€¡Ù…±Õ”€˜˜ÑåÁ•½˜Ù…±Õ”€ôôô€½‰©•Ðœ€˜˜€¹Õ±±…‰±”œ¥¸Ù…±Õ”¤É•ÑÕÉ¸€¡Ù…±Õ”…ÌìÉ•…‘½¹±ä¹Õ±±…‰±”üè‰½½±•…¸ô¤¹¹Õ±±…‰±”€ôôôÑÉÕ”ìÉ•ÑÕÉ¸™…±Í”ìô)™Õ¹Ñ¥½¸¥ÍA±…¥¹5…À¡Ù…±Õ”èÕ¹­¹½Ý¸¤èÙ…±Õ”¥ÌI•½ÉñÍÑÉ¥¹œ°Õ¹­¹½Ý¸øìÉ•ÑÕÉ¸	½½±•…¸¡Ù…±Õ”€˜˜ÑåÁ•½˜Ù…±Õ”€ôôô€½‰©•Ðœ€˜˜€…ÉÉ…ä¹¥ÍÉÉ…ä¡Ù…±Õ”¤€˜˜€„ ­¥¹œ¥¸Ù…±Õ”¤€˜˜€„ É•˜œ¥¸Ù…±Õ”¤€˜˜€…¥Íi½¡Ù…±Õ”¤¤ìô)™Õ¹Ñ¥½¸¥Í¹¥¹•I•˜¡Ù…±Õ”èÕ¹­¹½Ý¸¤èÙ…±Õ”¥Ì¹¥¹•I•˜ìÉ•ÑÕÉ¸	½½±•…¸¡Ù…±Õ”€˜˜ÑåÁ•½˜Ù…±Õ”€ôôô€½‰©•Ðœ€˜˜€¥œ¥¸Ù…±Õ”€˜˜€­¥¹œ¥¸Ù…±Õ”€˜˜=‰©•Ð¹Ù…±Õ•Ì¡I•™-¥¹¤¹¥¹±Õ‘•Ì ¡Ù…±Õ”…Ì¹¥¹•I•˜¤¹­¥¹¤¤ìô)™Õ¹Ñ¥½¸ÅÕ•ÉåI•˜¡Ù…±Õ”è¹¥¹•I•˜ðI•™UÍ…”¤è¹¥¹•I•˜ìÉ•ÑÕÉ¸¥ÍI•™UÍ…”¡Ù…±Õ”¤€üÙ…±Õ”¹É•˜€èÙ…±Õ”ìô)™Õ¹Ñ¥½¸¥ÍI•ÅÕ•ÍÑ	½‘åI•˜¡Ù…±Õ”èÕ¹­¹½Ý¸¤èÙ…±Õ”¥ÌI•ÅÕ•ÍÑ	½‘åI•˜ìÉ•ÑÕÉ¸¥Í¹¥¹•I•˜¡Ù…±Õ”¤€˜˜Ù…±Õ”¹­¥¹€ôôôI•™-¥¹¹É•ÅÕ•ÍÑ	½‘äìô)™Õ¹Ñ¥½¸¥ÍI•ÍÁ½¹Í•I•˜¡Ù…±Õ”èÕ¹­¹½Ý¸¤èÙ…±Õ”¥ÌI•ÍÁ½¹Í•I•˜ìÉ•ÑÕÉ¸¥Í¹¥¹•I•˜¡Ù…±Õ”¤€˜˜Ù…±Õ”¹­¥¹€ôôôI•™-¥¹¹É•ÍÁ½¹Í”ìô)™Õ¹Ñ¥½¸¥ÍM¡•µ…¹Ù•±½Á”¡Ù…±Õ”èÕ¹­¹½Ý¸¤èÙ…±Õ”¥ÌìÉ•…‘½¹±äÍ¡•µ„èÕ¹­¹½Ý¸ìÉ•…‘½¹±äÉ•ÅÕ¥É•üè‰½½±•…¸ìÉ•…‘½¹±ä‘•ÍÉ¥ÁÑ¥½¸üèÍÑÉ¥¹œìÉ•…‘½¹±ä½¹Ñ•¹ÑQåÁ”üèÍÑÉ¥¹œðÉ•…‘½¹±äÍÑÉ¥¹mtôìÉ•ÑÕÉ¸	½½±•…¸¡Ù…±Õ”€˜˜ÑåÁ•½˜Ù…±Õ”€ôôô€½‰©•Ðœ€˜˜€Í¡•µ„œ¥¸Ù…±Õ”¤ìô)™Õ¹Ñ¥½¸©½¥¹I½ÕÑ”¡‰…Í”èÍÑÉ¥¹œ°Á…Ñ èÍÑÉ¥¹œ¤èÍÑÉ¥¹œì½¹ÍÐ©½¥¹•€ô€‘í‰…Í”¹É•Á±…” ½p¼¼°€œœ¥ô¼‘íÁ…Ñ ¹É•Á±…” ½yp¼¼°€œœ¥õ€ìÉ•ÑÕÉ¸©½¥¹•¹ÍÑ…ÉÑÍ]¥Ñ  œ¼œ¤€ü©½¥¹•€è€¼‘í©½¥¹•‘õ€ìô)™Õ¹Ñ¥½¸µ…Á…É‘¥¹…±¥Ñä¡Ù…±Õ”èÍÑÉ¥¹œ¤è€½¹•Q½=¹”œð€½¹•Q½5…¹äœð€µ…¹åQ½=¹”œð€µ…¹åQ½5…¹äœì¥˜€¡Ù…±Õ”€ôôô€¡…Í=¹”œ¤É•ÑÕÉ¸€½¹•Q½=¹”œì¥˜€¡Ù…±Õ”€ôôô€¡…Í5…¹äœ¤É•ÑÕÉ¸€½¹•Q½5…¹äœì¥˜€¡Ù…±Õ”€ôôô€‰•±½¹ÍQ¼œ¤É•ÑÕÉ¸€µ…¹åQ½=¹”œìÉ•ÑÕÉ¸€µ…¹åQ½5…¹äœìô)™Õ¹Ñ¥½¸Ù…±¥‘…Ñ•=Á•É…Ñ¥½¹%‘Ì¡½Á•É…Ñ¥½¹ÌèÉ•…‘½¹±ä½µÁ¥±•‘=Á•É…Ñ¥½¹mt°‘¥…¹½ÍÑ¥Ìè¥…¹½ÍÑ¥mt¤èÙ½¥ì½¹ÍÐÍ••¸€ô¹•ÜM•ÐñÍÑÉ¥¹œø ¤ì™½È€¡½¹ÍÐ½Á•É…Ñ¥½¸½˜½Á•É…Ñ¥½¹Ì¤ì¥˜€¡Í••¸¹¡…Ì¡½Á•É…Ñ¥½¸¹½Á•É…Ñ¥½¹%¤¤‘¥…¹½ÍÑ¥Ì¹ÁÕÍ ¡•ÉÉ½È UQ!=I%9}UA1%Q}=AIQ%=8œ°ÕÁ±¥…Ñ”½Á•É…Ñ¥½¸%€ˆ‘í½Á•É…Ñ¥½¸¹½Á•É…Ñ¥½¹%‘ôˆ¹€¤¤ìÍ••¸¹…‘¡½Á•É…Ñ¥½¸¹½Á•É…Ñ¥½¹%¤ìôô)™Õ¹Ñ¥½¸Ù…±¥‘…Ñ•…¡•%¹Ù…±¥‘…Ñ¥½¹Ì¡½Á•É…Ñ¥½¹ÌèÉ•…‘½¹±ä½µÁ¥±•‘=Á•É…Ñ¥½¹mt°‘¥…¹½ÍÑ¥Ìè¥…¹½ÍÑ¥mt¤èÙ½¥ì½¹ÍÐ¥‘Ì€ô¹•ÜM•Ð¡½Á•É…Ñ¥½¹Ì¹µ…À ¡½Á•É…Ñ¥½¸¤€ôø½Á•É…Ñ¥½¸¹½Á•É…Ñ¥½¹%¤¤ì™½È€¡½¹ÍÐ½Á•É…Ñ¥½¸½˜½Á•É…Ñ¥½¹Ì¤™½È€¡½¹ÍÐÑ…É•Ð½˜½Á•É…Ñ¥½¸¹…¡•%¹Ù…±¥‘…Ñ•Ì¤¥˜€ …¥‘Ì¹¡…Ì¡Ñ…É•Ð¤¤‘¥…¹½ÍÑ¥Ì¹ÁÕÍ ¡•ÉÉ½È UQ!=I%9}!}=AIQ%=9}5%MM%9œ°=Á•É…Ñ¥½¸€ˆ‘í½Á•É…Ñ¥½¸¹½Á•É…Ñ¥½¹%‘ôˆ¥¹Ù…±¥‘…Ñ•ÌÕ¹­¹½Ý¸½Á•É…Ñ¥½¸€ˆ‘íÑ…É•Ñôˆ¹€¤¤ìô)™Õ¹Ñ¥½¸•ÉÉ½È¡½‘”èÍÑÉ¥¹œ°µ•ÍÍ…”èÍÑÉ¥¹œ¤è¥…¹½ÍÑ¥ŒìÉ•ÑÕÉ¸ì½‘”°Í•Ù•É¥Ñäè€•ÉÉ½Èœ°±…å•Èè€…ÕÑ¡½É¥¹œœ°µ•ÍÍ…”ôìô)™Õ¹Ñ¥½¸Ý…É¹¥¹œ¡½‘”èÍÑÉ¥¹œ°µ•ÍÍ…”èÍÑÉ¥¹œ¤è¥…¹½ÍÑ¥ŒìÉ•ÑÕÉ¸ì½‘”°Í•Ù•É¥Ñäè€Ý…É¹¥¹œœ°±…å•Èè€…ÕÑ¡½É¥¹œœ°µ•ÍÍ…”ôìô)™Õ¹Ñ¥½¸Ñ½)Í½¹Y…±Õ”¡Ù…±Õ”èÕ¹­¹½Ý¸¤è)Í½¹Y…±Õ”ì¥˜€¡Ù…±Õ”€ôôôÕ¹‘•™¥¹•¤É•ÑÕÉ¸¹Õ±°ìÉ•ÑÕÉ¸)M=8¹Á…ÉÍ”¡)M=8¹ÍÑÉ¥¹¥™ä¡Ù…±Õ”¤¤…Ì)Í½¹Y…±Õ”ìô)™Õ¹Ñ¥½¸Ñ½)Í½¹=‰©•Ð¡Ù…±Õ”èÕ¹­¹½Ý¸¤è)Í½¹=‰©•Ðì½¹ÍÐ½¹Ù•ÉÑ•€ôÑ½)Í½¹Y…±Õ”¡Ù…±Õ”¤ìÉ•ÑÕÉ¸½¹Ù•ÉÑ•€„ôô¹Õ±°€˜˜ÑåÁ•½˜½¹Ù•ÉÑ•€ôôô€½‰©•Ðœ€˜˜€…ÉÉ…ä¹¥ÍÉÉ…ä¡½¹Ù•ÉÑ•¤€ü½¹Ù•ÉÑ•…Ì)Í½¹=‰©•Ð€èìÙ…±Õ”è½¹Ù•ÉÑ•ôìô(