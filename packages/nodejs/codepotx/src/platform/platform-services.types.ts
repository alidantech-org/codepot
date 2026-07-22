import type {
  CachePort,
  ClockPort,
  CommandRunnerPort,
  DataCodecPort,
  EventBusPort,
  FileSystemPort,
  FileWriterPort,
  HashPort,
  IdPort,
  ModuleLoaderPort,
  PortablePath,
  SourceResolverPort,
} from '@/contract/index';

import type { MemorySourceRegistryPort } from './source-resolver.types';

export interface PlatformServices {
  readonly files: FileSystemPort;
  readonly writer: FileWriterPort;
  readonly data: DataCodecPort;
  readonly modules: ModuleLoaderPort;
  readonly sources: SourceResolverPort;
  readonly hashes: HashPort;
  readonly cache: CachePort;
  readonly commands: CommandRunnerPort;
  readonly clock: ClockPort;
  readonly ids: IdPort;
  readonly events: EventBusPort;
  readonly memorySources: MemorySourceRegistryPort;
}

export interface DefaultPlatformOptions {
  readonly projectRoot?: PortablePath;
  readonly cacheRoot?: PortablePath;
  readonly sourceCacheRoot?: PortablePath;
}
