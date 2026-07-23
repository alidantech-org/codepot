import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

import * as root from '../src/index';
import * as authoring from '../src/authoring/index';
import * as contract from '../src/contract/index';
import * as generation from '../src/generation/index';
import * as platform from '../src/platform/index';
import * as runtime from '../src/runtime/index';
import * as templating from '../src/templating/index';

const testsRoot = dirname(fileURLToPath(import.meta.url));
const sourceRoot = resolve(testsRoot, '../src');

const authoringValues = [
  'DefaultAuthoringCompiler',
  'DefaultAuthoringEngine',
  'EngineIdPart',
  'HttpMethod',
  'PropertyKind',
  'RefKind',
  'SchemaKind',
  'ZOD_COMPATIBILITY_FEATURES',
  'createAccessBuilder',
  'createAuthoringEngine',
  'createAuthoringState',
  'createEngineId',
  'createSchemaComponentRegistry',
  'createScopedId',
  'defineAccess',
  'defineBaseEntities',
  'defineCodepotConfig',
  'defineEntities',
  'defineEntityRelations',
  'defineFrontend',
  'defineHooks',
  'definePackageConfig',
  'defineParameters',
  'defineProperties',
  'defineRequestBodies',
  'defineResource',
  'defineResponses',
  'defineRoutes',
  'defineSchemas',
  'defineVersionContract',
  'isCodepotConfig',
  'isRefUsage',
  'normalizeInfo',
  'ownerFromResource',
  'schema',
  'withRefMethods',
  'z',
].sort();

function keys(value: object): readonly string[] {
  return Object.keys(value).sort();
}

test('published runtime value surfaces remain intentional', () => {
  const protocolValues = [
    'CODEPOT_ARTIFACT_VERSION',
    'CODEPOT_PROTOCOL_VERSION',
  ];
  assert.deepEqual(keys(contract), protocolValues);
  assert.deepEqual(keys(authoring), authoringValues);
  assert.deepEqual(keys(root), [...authoringValues, ...protocolValues].sort());
  assert.deepEqual(keys(runtime), [
    'CodepotRuntime',
    'RunContextStore',
    'composeDefaultCodepotRuntime',
    'createCodepotRuntime',
    'createDefaultCodepotRuntime',
  ]);
  assert.deepEqual(keys(platform), [
    'ChangedAwareFileWriter',
    'CodepotCancellationController',
    'CodepotCancellationSignal',
    'DefaultSourceResolver',
    'FileSystemCache',
    'FixedClock',
    'MemoryCache',
    'MemoryCommandRunner',
    'MemoryFileSystem',
    'MemoryModuleLoader',
    'MemorySourceRegistry',
    'NodeCommandRunner',
    'NodeFileSystem',
    'RandomIdProvider',
    'SequentialEventBus',
    'SequentialIdProvider',
    'Sha256Hash',
    'SystemClock',
    'TsxModuleLoader',
    'YamlJsonCodec',
    'createDefaultPlatformServices',
    'createMemoryPlatformServices',
  ]);
  assert.deepEqual(keys(templating), [
    'BUILTIN_TEMPLATE_HELPERS',
    'DefaultTemplatingEngine',
    'buildTemplateContext',
    'buildTemplateVariableCatalog',
    'collectTemplateReferences',
    'collectVariableEntries',
    'compilePathParts',
    'compilePathTokens',
    'createNameSet',
    'createTemplateRenderer',
    'createTemplatingEngine',
    'formatTemplateVariableCatalog',
    'resolveExpression',
    'resolveOutputTokens',
    'validatePathExpression',
    'validateTemplateContext',
    'validateTemplateReferences',
  ]);
  assert.deepEqual(keys(generation), [
    'DefaultGenerationEngine',
    'GenerationEventPublisher',
    'GenerationFileTransaction',
    'ManagedWriteError',
    'RelativeImportAdapter',
    'applyManagedWrite',
    'artifactReference',
    'buildGenerationManifest',
    'compileCodepotFile',
    'countGenerationFiles',
    'createGenerationEngine',
    'createGenerationReport',
    'createRelativeImportAdapter',
    'currentFileDigest',
    'executePlannedCommands',
    'findTask',
    'joinPath',
    'loadGenerationManifest',
    'manifestPath',
    'planClean',
    'planCommands',
    'planFiles',
    'readRenderedGenerationCache',
    'renderCacheKey',
    'staleManagedFiles',
    'taskCommands',
    'writeGenerationManifest',
    'writeRenderedGenerationCache',
  ]);
});

test('published entrypoint sources contain no wildcard exports', async () => {
  for (const path of [
    'index.ts',
    'contract/index.ts',
    'runtime/index.ts',
    'platform/index.ts',
    'authoring/index.ts',
    'templating/index.ts',
    'generation/index.ts',
  ]) {
    const value = await readFile(resolve(sourceRoot, path), 'utf8');
    assert.doesNotMatch(value, /export\s+(?:type\s+)?\*/u, `${path} must be curated`);
  }
});
