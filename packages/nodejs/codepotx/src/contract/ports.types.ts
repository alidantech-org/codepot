import type { FileWriteOutcome, VirtualFile } from './generation-artifact.types';
import type { FileCompareMode, FileLifecycleMode } from './template-artifact.types';
import type {
  Awaitable,
  CancellationSignal,
  ContentDigest,
  Disposable,
  IsoTimestamp,
  JsonValue,
  PortablePath,
} from './common.types';
import type { CodepotEvent, CodepotEventListener, CodepotEventType } from './events.types';
import type {
  AuthoringArtifactLoadRequest,
  AuthoringArtifactLoadResult,
  AuthoringCacheRequest,
  AuthoringCacheResult,
  AuthoringCompileRequest,
  AuthoringCompileResult,
  AuthoringInspectRequest,
  AuthoringInspectResult,
  AuthoringValidateRequest,
  AuthoringValidateResult,
  CodepotFileLoadRequest,
  CodepotFileLoadResult,
  GenerationCleanRequest,
  GenerationCleanResult,
  GenerationCommandRequest,
  GenerationCommandResult,
  GenerationExecuteRequest,
  GenerationExecuteResult,
  GenerationPlanRequest,
  GenerationPlanResult,
  GenerationRenderRequest,
  GenerationRenderResult,
  GenerationWriteRequest,
  GenerationWriteResult,
  TemplateContextRequest,
  TemplateContextResult,
  TemplateRenderRequest,
  TemplateRenderResult,
  TemplatingCompileRequest,
  TemplatingCompileResult,
  TemplatingLoadRequest,
  TemplatingLoadResult,
  TemplatingValidateRequest,
  TemplatingValidateResult,
} from './requests.types';
import type { ResolvedSource, SourceDescriptor, SourceFileReference } from './sources.types';

export type FileKind = 'file' | 'directory' | 'symbolicLink' | 'other';

export interface FileStat {
  readonly kind: FileKind;
  readonly size: number;
  readonly modifiedAt?: IsoTimestamp;
}

export interface DirectoryEntry {
  readonly name: string;
  readonly path: PortablePath;
  readonly kind: FileKind;
}

export interface GlobOptions {
  readonly cwd?: PortablePath;
  readonly absolute?: boolean;
  readonly includeDirectories?: boolean;
  readonly ignore?: readonly string[];
}

export interface RemoveOptions {
  readonly recursive?: boolean;
  readonly force?: boolean;
}

/** All engine filesystem access is inverted through this port. */
export interface FileSystemPort {
  readText(path: PortablePath): Promise<string>;
  readBase64(path: PortablePath): Promise<string>;
  writeText(path: PortablePath, content: string): Promise<void>;
  writeBase64(path: PortablePath, content: string): Promise<void>;
  exists(path: PortablePath): Promise<boolean>;
  stat(path: PortablePath): Promise<FileStat>;
  list(path: PortablePath): Promise<readonly DirectoryEntry[]>;
  glob(patterns: readonly string[], options?: GlobOptions): Promise<readonly PortablePath[]>;
  mkdir(path: PortablePath, options?: { readonly recursive?: boolean }): Promise<void>;
  remove(path: PortablePath, options?: RemoveOptions): Promise<void>;
  realpath(path: PortablePath): Promise<PortablePath>;
}

export interface CompareFileRequest {
  readonly path: PortablePath;
  readonly content: VirtualFile['content'];
  readonly compareMode: FileCompareMode;
}

export interface CompareFileResult {
  readonly exists: boolean;
  readonly changed: boolean;
  readonly previousDigest?: ContentDigest;
  readonly nextDigest: ContentDigest;
}

export interface WriteFileRequest extends CompareFileRequest {
  readonly lifecycle: FileLifecycleMode;
  readonly atomic?: boolean;
  readonly dryRun?: boolean;
}

export interface WriteBatchRequest {
  readonly files: readonly VirtualFile[];
  readonly root: PortablePath;
  readonly atomic?: boolean;
  readonly dryRun?: boolean;
}

/** Changed-aware writer used by generation after in-memory rendering. */
export interface FileWriterPort {
  compare(request: CompareFileRequest): Promise<CompareFileResult>;
  write(request: WriteFileRequest): Promise<FileWriteOutcome>;
  writeBatch(request: WriteBatchRequest): Promise<readonly FileWriteOutcome[]>;
}

export interface DataCodecPort {
  parseJson<T = JsonValue>(text: string): T;
  stringifyJson(value: JsonValue, options?: { readonly pretty?: boolean }): string;
  parseYaml<T = JsonValue>(text: string): T;
  stringifyYaml(value: JsonValue): string;
}

export interface ModuleLoadOptions {
  readonly projectRoot?: PortablePath;
  readonly tsconfigFile?: PortablePath;
  readonly cache?: boolean;
  readonly signal?: CancellationSignal;
}

export interface LoadedModule<TExports = unknown> {
  readonly entry: SourceFileReference;
  readonly files: readonly SourceFileReference[];
  readonly exports: TExports;
}

export interface ModuleLoaderPort {
  load<TExports = unknown>(
    entry: PortablePath,
    options?: ModuleLoadOptions,
  ): Promise<LoadedModule<TExports>>;
}

export interface SourceResolveOptions {
  readonly projectRoot?: PortablePath;
  readonly cache?: 'auto' | 'bypass' | 'refresh';
  readonly signal?: CancellationSignal;
}

export interface SourceResolverPort {
  resolve(
    source: SourceDescriptor,
    options?: SourceResolveOptions,
  ): Promise<ResolvedSource>;
}

export interface HashPort {
  text(value: string): Promise<ContentDigest>;
  base64(value: string): Promise<ContentDigest>;
  values(values: readonly JsonValue[]): Promise<ContentDigest>;
}

export interface CacheEntry<TValue extends JsonValue = JsonValue> {
  readonly key: string;
  readonly value: TValue;
  readonly digest?: ContentDigest;
  readonly createdAt: IsoTimestamp;
  readonly expiresAt?: IsoTimestamp;
}

export interface CachePort {
  get<TValue extends JsonValue = JsonValue>(key: string): Promise<CacheEntry<TValue> | null>;
  set<TValue extends JsonValue = JsonValue>(entry: CacheEntry<TValue>): Promise<void>;
  delete(key: string): Promise<boolean>;
  clear(namespace?: string): Promise<void>;
}

export interface CommandRequest {
  readonly command: string;
  readonly cwd: PortablePath;
  readonly environment: Readonly<Record<string, string>>;
  readonly optional?: boolean;
  readonly dryRun?: boolean;
  readonly verbose?: boolean;
  readonly signal?: CancellationSignal;
}

export interface CommandResult {
  readonly command: string;
  readonly cwd: PortablePath;
  readonly exitCode: number | null;
  readonly stdout: string;
  readonly stderr: string;
  readonly skipped: boolean;
}

export interface CommandRunnerPort {
  run(request: CommandRequest): Promise<CommandResult>;
}

export interface ClockPort {
  now(): IsoTimestamp;
  monotonicMilliseconds(): number;
}

export interface IdPort {
  create(prefix?: string): string;
}

/** Observational event channel. Domain control flow must not depend on listeners. */
export interface EventBusPort {
  publish(event: CodepotEvent): Awaitable<void>;
  subscribe(listener: CodepotEventListener): Disposable;
  subscribe<TType extends CodepotEventType>(
    type: TType,
    listener: CodepotEventListener<Extract<CodepotEvent, { readonly type: TType }>>,
  ): Disposable;
}

export interface AuthoringPort {
  compile(request: AuthoringCompileRequest): Promise<AuthoringCompileResult>;
  validate(request: AuthoringValidateRequest): Promise<AuthoringValidateResult>;
  inspect(request: AuthoringInspectRequest): Promise<AuthoringInspectResult>;
  loadArtifact(request: AuthoringArtifactLoadRequest): Promise<AuthoringArtifactLoadResult>;
  cache(request: AuthoringCacheRequest): Promise<AuthoringCacheResult>;
}

export interface TemplatingPort {
  load(request: TemplatingLoadRequest): Promise<TemplatingLoadResult>;
  validate(request: TemplatingValidateRequest): Promise<TemplatingValidateResult>;
  compile(request: TemplatingCompileRequest): Promise<TemplatingCompileResult>;
  createContext(request: TemplateContextRequest): Promise<TemplateContextResult>;
  render(request: TemplateRenderRequest): Promise<TemplateRenderResult>;
}

export interface GenerationPort {
  load(request: CodepotFileLoadRequest): Promise<CodepotFileLoadResult>;
  plan(request: GenerationPlanRequest): Promise<GenerationPlanResult>;
  render(request: GenerationRenderRequest): Promise<GenerationRenderResult>;
  write(request: GenerationWriteRequest): Promise<GenerationWriteResult>;
  clean(request: GenerationCleanRequest): Promise<GenerationCleanResult>;
  runCommands(request: GenerationCommandRequest): Promise<GenerationCommandResult>;
  execute(request: GenerationExecuteRequest): Promise<GenerationExecuteResult>;
}
