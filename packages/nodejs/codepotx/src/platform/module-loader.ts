import { extname, relative, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

import { tsImport } from 'tsx/esm/api';

import type {
  FileSystemPort,
  HashPort,
  LoadedModule,
  ModuleLoaderPort,
  ModuleLoadOptions,
  SourceFileReference,
} from '@/contract/index';

function languageFor(path: string): string | undefined {
  switch (extname(path).toLowerCase()) {
    case '.ts':
    case '.mts':
    case '.cts':
      return 'typescript';
    case '.js':
    case '.mjs':
    case '.cjs':
      return 'javascript';
    case '.json':
      return 'json';
    default:
      return undefined;
  }
}

export class TsxModuleLoader implements ModuleLoaderPort {
  readonly #files: FileSystemPort;
  readonly #hash: HashPort;
  readonly #cache = new Map<string, Promise<LoadedModule<unknown>>>();

  constructor(files: FileSystemPort, hash: HashPort) {
    this.#files = files;
    this.#hash = hash;
  }

  async load<TExports = unknown>(
    entry: string,
    options: ModuleLoadOptions = {},
  ): Promise<LoadedModule<TExports>> {
    const absoluteEntry = resolve(options.projectRoot ?? process.cwd(), entry);
    const cacheKey = `${absoluteEntry}\u0000${options.tsconfigFile ?? ''}`;
    if (options.cache) {
      const existing = this.#cache.get(cacheKey);
      if (existing) return existing as Promise<LoadedModule<TExports>>;
      const pending = this.#load<TExports>(absoluteEntry, options);
      this.#cache.set(cacheKey, pending as Promise<LoadedModule<unknown>>);
      return pending;
    }
    return this.#load<TExports>(absoluteEntry, options);
  }

  async #load<TExports>(absoluteEntry: string, options: ModuleLoadOptions): Promise<LoadedModule<TExports>> {
    options.signal?.throwIfAborted();
    const imported = new Set<string>([pathToFileURL(absoluteEntry).href]);
    const projectRoot = resolve(options.projectRoot ?? process.cwd());
    const parentURL = pathToFileURL(resolve(projectRoot, '__codepot_loader__.mjs')).href;
    const exports = await tsImport<TExports>(pathToFileURL(absoluteEntry).href, {
      parentURL,
      ...(options.tsconfigFile ? { tsconfig: resolve(projectRoot, options.tsconfigFile) } : {}),
      onImport: (file) => {
        imported.add(file);
      },
    });
    options.signal?.throwIfAborted();

    const references: SourceFileReference[] = [];
    for (const uri of [...imported].sort((left, right) => left.localeCompare(right))) {
      if (!uri.startsWith('file:')) continue;
      const path = fileURLToPath(uri);
      if (!await this.#files.exists(path)) continue;
      const digest = await this.#hash.base64(await this.#files.readBase64(path));
      const language = languageFor(path);
      references.push({
        id: digest,
        uri,
        path,
        rootRelativePath: relative(projectRoot, path).replaceAll('\\', '/'),
        ...(language ? { language } : {}),
        digest,
      });
    }

    const entryLanguage = languageFor(absoluteEntry);
    const entryReference = references.find((file) => resolve(file.path) === absoluteEntry) ?? {
      id: await this.#hash.text(absoluteEntry),
      uri: pathToFileURL(absoluteEntry).href,
      path: absoluteEntry,
      rootRelativePath: relative(projectRoot, absoluteEntry).replaceAll('\\', '/'),
      ...(entryLanguage ? { language: entryLanguage } : {}),
    };

    return {
      entry: entryReference,
      files: references,
      exports,
    };
  }
}
