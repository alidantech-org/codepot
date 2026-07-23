import { posix } from 'node:path';
import type {
  ClockPort,
  DirectoryEntry,
  FileStat,
  FileSystemPort,
  GlobOptions,
  PortablePath,
  RemoveOptions,
} from '@/contract/index';
import { matchesAnyGlob } from '../shared/path-utils';
import { SystemClock } from '../shared/system';

interface MemoryEntry {
  readonly kind: 'file' | 'directory';
  content?: string;
  modifiedAt: string;
}

function normalizeMemoryPath(path: PortablePath, cwd = '/'): PortablePath {
  const portablePath = path.replaceAll('\\', '/');
  const portableCwd = cwd.replaceAll('\\', '/');
  const absolute = portablePath.startsWith('/')
    ? portablePath
    : posix.join(portableCwd, portablePath);
  const normalized = posix.normalize(absolute);
  return normalized === '.' ? '/' : normalized;
}

export class MemoryFileSystem implements FileSystemPort {
  readonly #entries = new Map<PortablePath, MemoryEntry>();
  readonly #clock: ClockPort;

  constructor(clock: ClockPort = new SystemClock()) {
    this.#clock = clock;
    this.#entries.set('/', { kind: 'directory', modifiedAt: this.#clock.now() });
  }

  async readText(path: PortablePath): Promise<string> {
    return Buffer.from(this.#file(path).content ?? '', 'base64').toString('utf8');
  }

  async readBase64(path: PortablePath): Promise<string> {
    return this.#file(path).content ?? '';
  }

  async writeText(path: PortablePath, content: string): Promise<void> {
    await this.writeBase64(path, Buffer.from(content, 'utf8').toString('base64'));
  }

  async writeBase64(path: PortablePath, content: string): Promise<void> {
    const normalized = normalizeMemoryPath(path);
    this.#ensureParents(normalized);
    this.#entries.set(normalized, {
      kind: 'file',
      content,
      modifiedAt: this.#clock.now(),
    });
  }

  async exists(path: PortablePath): Promise<boolean> {
    return this.#entries.has(normalizeMemoryPath(path));
  }

  async stat(path: PortablePath): Promise<FileStat> {
    const normalized = normalizeMemoryPath(path);
    const entry = this.#entries.get(normalized);
    if (!entry) throw new Error(`Memory path does not exist: ${normalized}`);
    return {
      kind: entry.kind,
      size: entry.kind === 'file'
        ? Buffer.from(entry.content ?? '', 'base64').byteLength
        : 0,
      modifiedAt: entry.modifiedAt,
    };
  }

  async list(path: PortablePath): Promise<readonly DirectoryEntry[]> {
    const root = normalizeMemoryPath(path);
    const entry = this.#entries.get(root);
    if (!entry || entry.kind !== 'directory') {
      throw new Error(`Memory directory does not exist: ${root}`);
    }
    const prefix = root === '/' ? '/' : `${root}/`;
    const children = new Map<string, DirectoryEntry>();
    for (const [candidate, value] of this.#entries) {
      if (!candidate.startsWith(prefix) || candidate === root) continue;
      const remainder = candidate.slice(prefix.length);
      if (remainder.includes('/')) continue;
      children.set(remainder, { name: remainder, path: candidate, kind: value.kind });
    }
    return [...children.values()].sort((left, right) => left.name.localeCompare(right.name));
  }

  async glob(
    patterns: readonly string[],
    options: GlobOptions = {},
  ): Promise<readonly PortablePath[]> {
    const cwd = normalizeMemoryPath(options.cwd ?? '/');
    const results: PortablePath[] = [];
    for (const [candidate, entry] of this.#entries) {
      if (candidate === '/') continue;
      if (!options.includeDirectories && entry.kind === 'directory') continue;
      if (!candidate.startsWith(cwd === '/' ? '/' : `${cwd}/`) && candidate !== cwd) continue;
      const relative = posix.relative(cwd, candidate);
      if (!matchesAnyGlob(relative, patterns)) continue;
      if (options.ignore && matchesAnyGlob(relative, options.ignore)) continue;
      results.push(options.absolute ? candidate : relative);
    }
    return results.sort((left, right) => left.localeCompare(right));
  }

  async mkdir(
    path: PortablePath,
    options: { readonly recursive?: boolean } = {},
  ): Promise<void> {
    const normalized = normalizeMemoryPath(path);
    if (options.recursive) {
      this.#ensureParents(posix.join(normalized, '_placeholder'));
      if (!this.#entries.has(normalized)) {
        this.#entries.set(normalized, {
          kind: 'directory',
          modifiedAt: this.#clock.now(),
        });
      }
      return;
    }
    const parent = posix.dirname(normalized);
    if (!this.#entries.has(parent)) throw new Error(`Parent directory does not exist: ${parent}`);
    this.#entries.set(normalized, {
      kind: 'directory',
      modifiedAt: this.#clock.now(),
    });
  }

  async remove(path: PortablePath, options: RemoveOptions = {}): Promise<void> {
    const normalized = normalizeMemoryPath(path);
    const entry = this.#entries.get(normalized);
    if (!entry) {
      if (options.force) return;
      throw new Error(`Memory path does not exist: ${normalized}`);
    }
    if (entry.kind === 'directory') {
      const descendants = [...this.#entries.keys()].filter((candidate) =>
        candidate.startsWith(`${normalized}/`),
      );
      if (descendants.length > 0 && !options.recursive) {
        throw new Error(`Memory directory is not empty: ${normalized}`);
      }
      for (const descendant of descendants) this.#entries.delete(descendant);
    }
    if (normalized !== '/') this.#entries.delete(normalized);
  }

  async move(
    from: PortablePath,
    to: PortablePath,
    options: { readonly overwrite?: boolean } = {},
  ): Promise<void> {
    const source = normalizeMemoryPath(from);
    const destination = normalizeMemoryPath(to);
    const entry = this.#entries.get(source);
    if (!entry) throw new Error(`Memory path does not exist: ${source}`);
    if (this.#entries.has(destination) && !options.overwrite) {
      throw new Error(`Memory destination already exists: ${destination}`);
    }
    if (options.overwrite) {
      await this.remove(destination, { recursive: true, force: true });
    }
    this.#ensureParents(destination);
    const descendants = [...this.#entries.entries()]
      .filter(([candidate]) => candidate === source || candidate.startsWith(`${source}/`))
      .sort(([left], [right]) => left.length - right.length);
    for (const [candidate, value] of descendants) {
      this.#entries.set(`${destination}${candidate.slice(source.length)}`, { ...value });
    }
    for (const [candidate] of descendants.reverse()) this.#entries.delete(candidate);
  }

  async realpath(path: PortablePath): Promise<PortablePath> {
    const normalized = normalizeMemoryPath(path);
    if (!this.#entries.has(normalized)) {
      throw new Error(`Memory path does not exist: ${normalized}`);
    }
    return normalized;
  }

  #file(path: PortablePath): MemoryEntry {
    const normalized = normalizeMemoryPath(path);
    const entry = this.#entries.get(normalized);
    if (!entry || entry.kind !== 'file') {
      throw new Error(`Memory file does not exist: ${normalized}`);
    }
    return entry;
  }

  #ensureParents(path: PortablePath): void {
    let current = posix.dirname(path);
    const missing: string[] = [];
    while (current !== '/' && !this.#entries.has(current)) {
      missing.push(current);
      current = posix.dirname(current);
    }
    for (const directory of missing.reverse()) {
      this.#entries.set(directory, {
        kind: 'directory',
        modifiedAt: this.#clock.now(),
      });
    }
  }
}
