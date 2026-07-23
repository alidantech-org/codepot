import type { CacheEntry, CachePort, ClockPort } from '@/contract/index';

function expired(entry: CacheEntry, now: string): boolean {
  return entry.expiresAt !== undefined && Date.parse(entry.expiresAt) <= Date.parse(now);
}

export class MemoryCache implements CachePort {
  readonly #entries = new Map<string, CacheEntry>();
  readonly #clock: ClockPort;

  constructor(clock: ClockPort) {
    this.#clock = clock;
  }

  async get(key: string): Promise<CacheEntry | null> {
    const entry = this.#entries.get(key);
    if (!entry) return null;
    if (expired(entry, this.#clock.now())) {
      this.#entries.delete(key);
      return null;
    }
    return structuredClone(entry);
  }

  async set(entry: CacheEntry): Promise<void> {
    this.#entries.set(entry.key, structuredClone(entry));
  }

  async delete(key: string): Promise<boolean> {
    return this.#entries.delete(key);
  }

  async clear(namespace?: string): Promise<void> {
    if (!namespace) {
      this.#entries.clear();
      return;
    }
    for (const key of this.#entries.keys()) {
      if (key.startsWith(namespace)) this.#entries.delete(key);
    }
  }
}
