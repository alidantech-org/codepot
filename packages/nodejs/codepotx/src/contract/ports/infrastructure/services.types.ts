import type {
  CancellationSignal,
  ContentDigest,
  IsoTimestamp,
  JsonValue,
  PortablePath,
} from '../../protocol/common.types';
import type {
  ResolvedSource,
  SourceDescriptor,
  SourceFileReference,
} from '../../sources/source.types';

export interface DataCodecPort {
  parseJson<T = JsonValue>(text: string): T;
  stringifyJson(value: unknown, options?: { readonly pretty?: boolean }): string;
  parseYaml<T = JsonValue>(text: string): T;
  stringifyYaml(value: unknown): string;
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

export interface CachePayload {
  readonly encoding: 'utf8' | 'base64';
  readonly data: string;
}

export interface CacheEntry {
  readonly key: string;
  readonly value: CachePayload;
  readonly digest?: ContentDigest;
  readonly createdAt: IsoTimestamp;
  readonly expiresAt?: IsoTimestamp;
}

export interface CachePort {
  get(key: string): Promise<CacheEntry | null>;
  set(entry: CacheEntry): Promise<void>;
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
