import type { AuthoringPort, CachePort, ClockPort, DataCodecPort, EventBusPort, FileSystemPort, HashPort, ModuleLoaderPort, SourceResolverPort } from '@/contract/index';
import type { AuthoringCompiler } from '../compiler/compiler.types';
export interface AuthoringEngineDependencies { readonly files: FileSystemPort; readonly sources: SourceResolverPort; readonly modules: ModuleLoaderPort; readonly hashes: HashPort; readonly cache: CachePort; readonly data: DataCodecPort; readonly clock: ClockPort; readonly events: EventBusPort; readonly compiler: AuthoringCompiler; }
export interface AuthoringEngine extends AuthoringPort {}
