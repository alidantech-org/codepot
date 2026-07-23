import type { ResolvedSource } from '@/contract/index';

export interface MemorySourceRegistryPort {
  get(id: string): ResolvedSource | null;
  register(source: ResolvedSource): void;
  delete(id: string): boolean;
}

export interface DefaultSourceResolverOptions {
  readonly cacheRoot: string;
  readonly memory: MemorySourceRegistryPort;
}
