import type { ResolvedSource } from '@/contract/index';
import type { MemorySourceRegistryPort } from '../shared/source-resolver.types';

export class MemorySourceRegistry implements MemorySourceRegistryPort {
  readonly #entries = new Map<string, ResolvedSource>();

  get(id: string): ResolvedSource | null {
    return this.#entries.get(id) ?? null;
  }

  register(source: ResolvedSource): void {
    this.#entries.set(source.id, structuredClone(source));
  }

  delete(id: string): boolean {
    return this.#entries.delete(id);
  }
}
