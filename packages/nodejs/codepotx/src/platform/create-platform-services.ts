import { resolve } from 'node:path';

import { FileSystemCache, MemoryCache } from './cache';
import { NodeCommandRunner } from './command-runner';
import { MemoryCommandRunner } from './memory-command-runner';
import { YamlJsonCodec } from './data-codec';
import { SequentialEventBus } from './event-bus';
import { ChangedAwareFileWriter } from './file-writer';
import { Sha256Hash } from './hash';
import { MemoryFileSystem } from './memory-file-system';
import { MemoryModuleLoader } from './memory-module-loader';
import { TsxModuleLoader } from './module-loader';
import { NodeFileSystem } from './node-file-system';
import type { DefaultPlatformOptions, PlatformServices } from './platform-services.types';
import { DefaultSourceResolver, MemorySourceRegistry } from './source-resolver';
import { RandomIdProvider, SequentialIdProvider, SystemClock } from './system';

export function createDefaultPlatformServices(
  options: DefaultPlatformOptions = {},
): PlatformServices {
  const projectRoot = resolve(options.projectRoot ?? process.cwd());
  const cacheRoot = resolve(projectRoot, options.cacheRoot ?? '.codepot/cache');
  const sourceCacheRoot = resolve(projectRoot, options.sourceCacheRoot ?? '.codepot/sources');
  const files = new NodeFileSystem();
  const data = new YamlJsonCodec();
  const hashes = new Sha256Hash();
  const clock = new SystemClock();
  const ids = new RandomIdProvider();
  const events = new SequentialEventBus();
  const commands = new NodeCommandRunner();
  const memorySources = new MemorySourceRegistry();
  const cache = new FileSystemCache(cacheRoot, files, data, hashes, clock);
  const writer = new ChangedAwareFileWriter(files, hashes, ids);
  const modules = new TsxModuleLoader(files, hashes);
  const sources = new DefaultSourceResolver(files, hashes, data, commands, {
    cacheRoot: sourceCacheRoot,
    memory: memorySources,
  });

  return {
    files,
    writer,
    data,
    modules,
    sources,
    hashes,
    cache,
    commands,
    clock,
    ids,
    events,
    memorySources,
  };
}

export function createMemoryPlatformServices(): PlatformServices {
  const clock = new SystemClock();
  const ids = new SequentialIdProvider();
  const files = new MemoryFileSystem(clock);
  const data = new YamlJsonCodec();
  const hashes = new Sha256Hash();
  const events = new SequentialEventBus();
  const commands = new MemoryCommandRunner();
  const memorySources = new MemorySourceRegistry();
  const cache = new MemoryCache(clock);
  const writer = new ChangedAwareFileWriter(files, hashes, ids);
  const modules = new MemoryModuleLoader();
  const sources = new DefaultSourceResolver(files, hashes, data, commands, {
    cacheRoot: '/.codepot/sources',
    memory: memorySources,
  });

  return {
    files,
    writer,
    data,
    modules,
    sources,
    hashes,
    cache,
    commands,
    clock,
    ids,
    events,
    memorySources,
  };
}
