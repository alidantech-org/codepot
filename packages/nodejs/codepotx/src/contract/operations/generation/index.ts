import type { CompiledAuthoringArtifact } from '../../artifacts/authoring/index';
import type {
  CommandExecutionOutcome,
  FileWriteOutcome,
  GenerationPlan,
  GenerationResult,
  RenderedGeneration,
} from '../../artifacts/generation/index';
import type { CompiledTemplatePack } from '../../artifacts/templating/index';
import type { OperationResult } from '../../diagnostics/index';
import type {
  CancellationSignal,
  JsonObject,
  PortablePath,
} from '../../protocol/common.types';
import type { SourceDescriptor } from '../../sources/source.types';
import type { CacheMode } from '../cache-mode.types';

export interface CodepotFileLoadRequest {
  readonly source?: SourceDescriptor;
  readonly projectRoot?: PortablePath;
  readonly file?: PortablePath;
}

export interface CodepotCommandConfig {
  readonly name?: string;
  readonly run: string;
  readonly cwd?: PortablePath;
  readonly optional?: boolean;
  readonly environment?: Readonly<Record<string, string>>;
}

export interface CodepotTaskConfig {
  readonly name: string;
  readonly description?: string;
  readonly authoring: SourceDescriptor;
  readonly templates: SourceDescriptor;
  readonly output: PortablePath;
  readonly clean: readonly PortablePath[];
  readonly before: readonly CodepotCommandConfig[];
  readonly after: readonly CodepotCommandConfig[];
  readonly environment: Readonly<Record<string, string>>;
  readonly variables?: JsonObject;
  readonly frontend?: string;
  readonly transactional: boolean;
  readonly manifest?: PortablePath;
}

export interface CompiledCodepotFile {
  readonly path: PortablePath;
  readonly root: PortablePath;
  readonly allow: boolean;
  readonly defaults: JsonObject;
  readonly tasks: readonly CodepotTaskConfig[];
}

export interface GenerationPlanRequest {
  readonly codepotFile: CompiledCodepotFile;
  readonly task: string;
  readonly authoring?: CompiledAuthoringArtifact;
  readonly templates?: CompiledTemplatePack;
  readonly refresh?: boolean;
  readonly dryRun?: boolean;
  readonly skipBefore?: boolean;
  readonly skipAfter?: boolean;
  readonly signal?: CancellationSignal;
}

export interface GenerationRenderRequest {
  readonly plan: GenerationPlan;
  readonly templates: CompiledTemplatePack;
  readonly cache?: CacheMode;
  readonly signal?: CancellationSignal;
}

export interface GenerationWriteRequest {
  readonly rendered: RenderedGeneration;
  readonly outputRoot: PortablePath;
  readonly dryRun?: boolean;
  readonly atomic?: boolean;
  readonly signal?: CancellationSignal;
}

export interface GenerationCleanRequest {
  readonly plan: GenerationPlan;
  readonly dryRun?: boolean;
  readonly signal?: CancellationSignal;
}

export interface GenerationCommandRequest {
  readonly plan: GenerationPlan;
  readonly phase: 'before' | 'after';
  readonly dryRun?: boolean;
  readonly verbose?: boolean;
  readonly signal?: CancellationSignal;
}

export interface GenerationExecuteRequest {
  readonly codepotFile?: CodepotFileLoadRequest;
  readonly task?: string;
  readonly allTasks?: boolean;
  readonly dryRun?: boolean;
  readonly refresh?: boolean;
  readonly skipBefore?: boolean;
  readonly skipAfter?: boolean;
  readonly verbose?: boolean;
  readonly signal?: CancellationSignal;
}

export type CodepotFileLoadResult = OperationResult<CompiledCodepotFile>;
export type GenerationPlanResult = OperationResult<GenerationPlan>;
export type GenerationRenderResult = OperationResult<RenderedGeneration>;
export type GenerationWriteResult = OperationResult<readonly FileWriteOutcome[]>;
export type GenerationCleanResult = OperationResult<readonly PortablePath[]>;
export type GenerationCommandResult = OperationResult<readonly CommandExecutionOutcome[]>;
export type GenerationExecuteResult = OperationResult<readonly GenerationResult[]>;
