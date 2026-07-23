import { resolve } from 'node:path';
import type {
  LoadedModule,
  ModuleLoaderPort,
  ModuleLoadOptions,
  SourceFileReference,
} from '@/contract/index';

export class MemoryModuleLoader implements ModuleLoaderPort {
  readonly #modules = new Map<string, LoadedModule<unknown>>();

  register<TExports>(
    entry: string,
    exports: TExports,
    files: readonly SourceFileReference[] = [],
  ): void {
    const absoluteEntry = resolve(entry);
    const entryReference = files.find((file) => resolve(file.path) === absoluteEntry) ?? {
      id: absoluteEntry,
      uri: `memory://${absoluteEntry}`,
      path: absoluteEntry,
    };
    this.#modules.set(absoluteEntry, { entry: entryReference, files, exports });
  }

  async load<TExports = unknown>(
    entry: string,
    options: ModuleLoadOptions = {},
  ): Promise<LoadedModule<TExports>> {
    options.signal?.throwIfAborted();
    const absoluteEntry = resolve(options.projectRoot ?? process.cwd(), entry);
    const loaded = this.#modules.get(absoluteEntry);
    if (!loaded) throw new Error(`Unknown memory module: ${absoluteEntry}`);
    return loaded as LoadedModule<TExports>;
  }
}
