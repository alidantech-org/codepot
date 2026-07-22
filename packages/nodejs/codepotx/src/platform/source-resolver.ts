import { createRequire } from 'node:module';
import { basename, dirname, extname, join, parse, relative, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

import type {
  CommandRunnerPort,
  DataCodecPort,
  FileSystemPort,
  HashPort,
  ResolvedSource,
  SourceDescriptor,
  SourceFileReference,
  SourceResolveOptions,
  SourceResolverPort,
} from '@/contract/index';

import { OperationCancelledError, PlatformOperationError } from './errors';
import type { DefaultSourceResolverOptions, MemorySourceRegistryPort } from './source-resolver.types';

function quote(value: string): string {
  return `"${value.replaceAll('"', '\\"')}"`;
}

function languageFor(path: string): string | undefined {
  const extension = extname(path).slice(1).toLowerCase();
  return extension || undefined;
}

export class MemorySourceRegistry implements MemorySourceRegistryPort {
  readonly #sources = new Map<string, ResolvedSource>();

  get(id: string): ResolvedSource | null {
    return this.#sources.get(id) ?? null;
  }

  register(source: ResolvedSource): void {
    this.#sources.set(source.id, structuredClone(source));
  }

  delete(id: string): boolean {
    return this.#sources.delete(id);
  }
}

export class DefaultSourceResolver implements SourceResolverPort {
  readonly #files: FileSystemPort;
  readonly #hash: HashPort;
  readonly #codec: DataCodecPort;
  readonly #commands: CommandRunnerPort;
  readonly #options: DefaultSourceResolverOptions;

  constructor(
    files: FileSystemPort,
    hash: HashPort,
    codec: DataCodecPort,
    commands: CommandRunnerPort,
    options: DefaultSourceResolverOptions,
  ) {
    this.#files = files;
    this.#hash = hash;
    this.#codec = codec;
    this.#commands = commands;
    this.#options = options;
  }

  async resolve(source: SourceDescriptor, options: SourceResolveOptions = {}): Promise<ResolvedSource> {
    options.signal?.throwIfAborted();

    switch (source.kind) {
      case 'memory': {
        const resolved = this.#options.memory.get(source.id);
        if (!resolved) throw new PlatformOperationError('MEMORY_SOURCE_MISSING', `Unknown memory source: ${source.id}`);
        return structuredClone(resolved);
      }
      case 'local':
        return this.#resolveLocal(source, options.projectRoot);
      case 'artifact':
        return this.#resolveArtifact(source, options.projectRoot);
      case 'package':
        return this.#resolvePackage(source, options.projectRoot);
      case 'git':
        return this.#resolveGit(source, options);
    }
  }

  async #resolveLocal(
    source: Extract<SourceDescriptor, { readonly kind: 'local' }>,
    projectRoot = process.cwd(),
  ): Promise<ResolvedSource> {
    const selected = resolve(projectRoot, source.path);
    const selectedStat = await this.#files.stat(selected);
    const root = selectedStat.kind === 'directory' ? selected : dirname(selected);
    const entry = source.entry ? resolve(root, source.entry) : selected;
    return this.#describe(source, root, entry);
  }

  async #resolveArtifact(
    source: Extract<SourceDescriptor, { readonly kind: 'artifact' }>,
    projectRoot = process.cwd(),
  ): Promise<ResolvedSource> {
    const entry = resolve(projectRoot, source.path);
    return this.#describe(source, dirname(entry), entry);
  }

  async #resolvePackage(
    source: Extract<SourceDescriptor, { readonly kind: 'package' }>,
    projectRoot = process.cwd(),
  ): Promise<ResolvedSource> {
    const require = createRequire(join(resolve(projectRoot), 'package.json'));
    let resolvedEntry: string;
    try {
      resolvedEntry = require.resolve(source.package);
    } catch (error) {
      throw new PlatformOperationError('PACKAGE_SOURCE_MISSING', `Unable to resolve package: ${source.package}`, { cause: error });
    }

    const packageRoot = await this.#findPackageRoot(resolvedEntry, source.package);
    const manifest = this.#codec.parseJson<{ readonly name?: string; readonly version?: string }>(
      await this.#files.readText(join(packageRoot, 'package.json')),
    );
    if (source.version && manifest.version !== source.version) {
      throw new PlatformOperationError(
        'PACKAGE_VERSION_MISMATCH',
        `Package ${source.package} resolved to ${manifest.version ?? 'unknown'}, expected ${source.version}.`,
      );
    }

    const root = source.path ? resolve(packageRoot, source.path) : packageRoot;
    const entry = source.entry ? resolve(root, source.entry) : root;
    return this.#describe(source, root, entry);
  }

  async #resolveGit(
    source: Extract<SourceDescriptor, { readonly kind: 'git' }>,
    options: SourceResolveOptions,
  ): Promise<ResolvedSource> {
    const key = await this.#hash.values([
      source.repository,
      source.ref ?? 'HEAD',
      source.path ?? '',
    ]);
    const cloneRoot = resolve(this.#options.cacheRoot, 'git', key);

    if (options.cache === 'refresh' && await this.#files.exists(cloneRoot)) {
      await this.#files.remove(cloneRoot, { recursive: true, force: true });
    }

    if (!await this.#files.exists(cloneRoot) || options.cache === 'bypass') {
      const target = options.cache === 'bypass'
        ? resolve(this.#options.cacheRoot, 'git', `${key}-bypass`)
        : cloneRoot;
      await this.#files.remove(target, { recursive: true, force: true });
      await this.#files.mkdir(dirname(target), { recursive: true });
      await this.#runGit(`git clone --no-checkout ${quote(source.repository)} ${quote(target)}`, dirname(target), options);
      if (source.ref) {
        await this.#runGit(`git -C ${quote(target)} fetch --depth 1 origin ${quote(source.ref)}`, target, options);
        await this.#runGit(`git -C ${quote(target)} checkout --detach FETCH_HEAD`, target, options);
      } else {
        await this.#runGit(`git -C ${quote(target)} checkout --detach`, target, options);
      }
      if (options.cache === 'bypass') {
        const root = source.path ? resolve(target, source.path) : target;
        const entry = source.entry ? resolve(root, source.entry) : root;
        return this.#describe(source, root, entry);
      }
    }

    const root = source.path ? resolve(cloneRoot, source.path) : cloneRoot;
    const entry = source.entry ? resolve(root, source.entry) : root;
    return this.#describe(source, root, entry);
  }

  async #runGit(command: string, cwd: string, options: SourceResolveOptions): Promise<void> {
    options.signal?.throwIfAborted();
    const result = await this.#commands.run({
      command,
      cwd,
      environment: {},
      ...(options.signal ? { signal: options.signal } : {}),
    });
    if (result.exitCode !== 0) {
      if (options.signal?.aborted) throw new OperationCancelledError(options.signal.reason);
      throw new PlatformOperationError('GIT_COMMAND_FAILED', `${command}\n${result.stderr || result.stdout}`);
    }
  }

  async #findPackageRoot(entry: string, expectedName: string): Promise<string> {
    let current = dirname(entry);
    const root = parse(current).root;
    while (current !== root) {
      const manifestPath = join(current, 'package.json');
      if (await this.#files.exists(manifestPath)) {
        try {
          const manifest = this.#codec.parseJson<{ readonly name?: string }>(await this.#files.readText(manifestPath));
          if (manifest.name === expectedName) return current;
        } catch {
          // Continue walking if a nested package manifest is not the selected package.
        }
      }
      current = dirname(current);
    }
    throw new PlatformOperationError('PACKAGE_ROOT_MISSING', `Unable to locate package root for ${expectedName}.`);
  }

  async #describe(source: SourceDescriptor, root: string, entry: string): Promise<ResolvedSource> {
    if (!await this.#files.exists(root)) {
      throw new PlatformOperationError('SOURCE_ROOT_MISSING', `Source root does not exist: ${root}`);
    }
    if (!await this.#files.exists(entry)) {
      throw new PlatformOperationError('SOURCE_ENTRY_MISSING', `Source entry does not exist: ${entry}`);
    }

    const rootStat = await this.#files.stat(root);
    const paths = rootStat.kind === 'file'
      ? [root]
      : await this.#files.glob(['**/*'], {
          cwd: root,
          absolute: true,
          ignore: ['.git/**', 'node_modules/**', '.codepot/**'],
        });
    const references: SourceFileReference[] = [];

    for (const path of [...paths].sort((left, right) => left.localeCompare(right))) {
      const value = await this.#files.stat(path);
      if (value.kind !== 'file') continue;
      const digest = await this.#hash.base64(await this.#files.readBase64(path));
      const language = languageFor(path);
      references.push({
        id: digest,
        uri: pathToFileURL(path).href,
        path,
        rootRelativePath: relative(root, path).replaceAll('\\', '/') || basename(path),
        ...(language ? { language } : {}),
        digest,
      });
    }

    const digest = await this.#hash.values(references.map((file) => [file.rootRelativePath ?? file.path, file.digest ?? '']));
    return {
      id: await this.#hash.text(`${source.kind}:${entry}:${digest}`),
      descriptor: source,
      root,
      entry,
      digest,
      files: references,
    };
  }
}
