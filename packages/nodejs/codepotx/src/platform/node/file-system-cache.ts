import { join } from 'node:path';
import type {
  CacheEntry,
  CachePort,
  ClockPort,
  DataCodecPort,
  FileSystemPort,
  HashPort,
  PortablePath,
} from '@/contract/index';

function expired(entry: CacheEntry, now: string): boolean {
  return entry.expiresAt !== undefined && Date.parse(entry.expiresAt) <= Date.parse(now);
}

export class FileSystemCache implements CachePort {
  readonly #root: PortablePath;
  readonly #files: FileSystemPort;
  readonly #codec: DataCodecPort;
  readonly #hash: HashPort;
  readonly #clock: ClockPort;

  constructor(
    root: PortablePath,
    files: FileSystemPort,
    codec: DataCodecPort,
    hash: HashPort,
    clock: ClockPort,
  ) {
    this.#root = root;
    this.#files = files;
    this.#codec = codec;
    this.#hash = hash;
    this.#clock = clock;
  }

  async get(key: string): Promise<CacheEntry | null> {
    const path = await this.#pathFor(key);
    if (!await this.#files.exists(path)) return null;
    const entry = this.#codec.parseJson<CacheEntry>(await this.#files.readText(path));
    if (entry.key !== key) return null;
    if (expired(entry, this.#clock.now())) {
      await this.#files.remove(path, { force: true });
      return null;
    }
    return entry;
  }

  async set(entry: CacheEntry): Promise<void> {
    await this.#files.writeText(
      await this.#pathFor(entry.key),
      this.#codec.stringifyJson(entry),
    );
  }

  async delete(key: string): Promise<boolean> {
    const path = await this.#pathFor(key);
    if (!await this.#files.exists(path)) return false;
    await this.#files.remove(path, { force: true });
    return true;
  }

  async clear(namespace?: string): Promise<void> {
    if (!await this.#files.exists(this.#root)) return;
    const paths = await this.#files.glob(['**/*.json'], {
      cwd: this.#root,
      absolute: true,
    });
    for (const path of paths) {
      if (!namespace) {
        await this.#files.remove(path, { force: true });
        continue;
      }
      try {
        const entry = this.#codec.parseJson<CacheEntry>(await this.#files.readText(path));
        if (entry.key.startsWith(namespace)) await this.#files.remove(path, { force: true });
      } catch {
        // Malformed entries remain until a full clear.
      }
    }
  }

  async #pathFor(key: string): Promise<PortablePath> {
    return join(this.#root, `${await this.#hash.text(key)}.json`);
  }
}
