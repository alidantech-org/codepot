import {
  defineProperties,
  defineVersionContract,
  schema,
  z,
} from 'codepotx';
import type {
  CodepotConfig,
  CompiledAuthoringArtifact,
  CompiledPathToken,
  RouteDefinition,
} from 'codepotx';
import type {
  ArtifactHeader,
  CompiledPathToken as ContractCompiledPathToken,
  RuntimeRequest,
  RuntimeResponse,
} from 'codepotx/contract';
import {
  CodepotRuntime,
  createDefaultCodepotRuntime,
  RunContextStore,
} from 'codepotx/runtime';
import type { RuntimeDependencies } from 'codepotx/runtime';
import {
  createMemoryPlatformServices,
  MemoryFileSystem,
  NodeFileSystem,
} from 'codepotx/platform';
import type { PlatformServices } from 'codepotx/platform';
import {
  DefaultAuthoringCompiler,
  defineCodepotConfig,
} from 'codepotx/authoring';
import type { AuthoringCompiler } from 'codepotx/authoring';
import {
  compilePathTokens,
  createTemplatingEngine,
} from 'codepotx/templating';
import type { TemplatingDependencies } from 'codepotx/templating';
import {
  createGenerationEngine,
  planFiles,
} from 'codepotx/generation';
import type {
  GenerationDependencies,
  GenerationImportAdapter,
} from 'codepotx/generation';

const values = [
  defineProperties,
  defineVersionContract,
  schema,
  z,
  CodepotRuntime,
  createDefaultCodepotRuntime,
  RunContextStore,
  createMemoryPlatformServices,
  MemoryFileSystem,
  NodeFileSystem,
  DefaultAuthoringCompiler,
  defineCodepotConfig,
  compilePathTokens,
  createTemplatingEngine,
  createGenerationEngine,
  planFiles,
];
void values;

type PublicTypes = [
  CodepotConfig,
  CompiledAuthoringArtifact,
  CompiledPathToken,
  ContractCompiledPathToken,
  RouteDefinition,
  ArtifactHeader<'codepot.authoring'>,
  RuntimeRequest<'authoring.compile'>,
  RuntimeResponse<'generation.execute'>,
  RuntimeDependencies,
  PlatformServices,
  AuthoringCompiler,
  TemplatingDependencies,
  GenerationDependencies,
  GenerationImportAdapter,
];

export type { PublicTypes };
