import type { CancellationSignal, JsonObject, PortablePath } from './common.types';
import type { CompiledAuthoringArtifact } from './authoring-artifact.types';
import type {
  CommandExecutionOutcome,
  FileWriteOutcome,
  GenerationPlan,
  GenerationResult,
  RenderedGeneration,
  VirtualFile,
} from './generation-artifact.types';
import type { CompiledTemplatePack } from './template-artifact.types';
import type {
  TemplateContextValidation,
  TemplateVariableCatalog,
} from './template-variables.types';
import type { OperationResult, ValidationResult } from './diagnostics.types';
import type { SourceDescriptor } from './sources.types';

export type CacheMode = 'auto' | 'bypass' | 'refresh';

export interface AuthoringCompileRequest {
  readonly source: SourceDescriptor;
  readonly projectRoot?: PortablePath;
  readonly configFile?: PortablePath;
  readonly tsconfigFile?: PortablePath;
  readonly cache?: CacheMode;
  readonly typecheck?: boolean;
  readonly includeDebugMetadata?: boolean;
}

export interface AuthoringValidateRequest {
  readonly source: SourceDescriptor;
  readonly projectRoot?: PortablePath;
  readonly configFile?: PortablePath;
  readonly tsconfigFile?: PortablePath;
  readonly typecheck?: boolean;
}

export interface AuthoringInspectRequest extends AuthoringCompileRequest {
  readonly format?: 'object' | 'json';
  readonly pretty?: boolean;
}

export interface AuthoringArtifactLoadRequest {
  readonly source: SourceDescriptor;
  readonly verifyDigest?: boolean;
}

export interface AuthoringCacheRequest {
  readonly source: SourceDescriptor;
  readonly operation: 'read' | 'write' | 'invalidate';
  readonly artifact?: CompiledAuthoringArtifact;
}

export type AuthoringCompileResult = OperationResult<CompiledAuthoringArtifact>;
export type AuthoringValidateResult = OperationResult<ValidationResult>;
export type AuthoringInspectResult = OperationResult<CompiledAuthoringArtifact | string>;
export type AuthoringArtifactLoadResult = OperationResult<CompiledAuthoringArtifact>;
export type AuthoringCacheResult = OperationResult<CompiledAuthoringArtifact | null>;

export interface TemplatingLoadRequest {
  readonly source: SourceDescriptor;
  readonly projectRoot?: PortablePath;
  readonly pathsFile?: PortablePath;
  readonly cache?: CacheMode;
}

export interface TemplatingValidateRequest extends TemplatingLoadRequest {}
export interface TemplatingCompileRequest extends TemplatingLoadRequest {}

export interface TemplateContextRequest {
  readonly authoring: CompiledAuthoringArtifact;
  readonly templates: CompiledTemplatePack;
  readonly project?: JsonObject;
  readonly selectedFrontend?: string;
  readonly variables?: JsonObject;
  readonly language?: JsonObject;
  readonly emit?: JsonObject;
  readonly file?: JsonObject;
}

export interface TemplateVariablesRequest extends TemplateContextRequest {
  readonly format?: 'object' | 'json' | 'markdown';
  readonly pretty?: boolean;
}

export interface TemplateContextValidateRequest extends TemplateContextRequest {
  readonly strict?: boolean;
}

export interface TemplateRenderRequest {
  readonly templates: CompiledTemplatePack;
  readonly files: readonly {
    readonly templateId: string;
    readonly outputPath: PortablePath;
    readonly context: JsonObject;
  }[];
}

export type TemplatingLoadResult = OperationResult<CompiledTemplatePack>;
export type TemplatingValidateResult = OperationResult<ValidationResult>;
export type TemplatingCompileResult = OperationResult<CompiledTemplatePack>;
export type TemplateContextResult = OperationResult<JsonObject>;
export type TemplateVariablesResult = OperationResult<TemplateVariableCatalog | string>;
export type TemplateContextValidateResult = OperationResult<TemplateContextValidation>;
export type TemplateRenderResult = OperationResult<readonly VirtualFile[]>;

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
