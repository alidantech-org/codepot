import assert from 'node:assert/strict';
import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';

import type { CodepotEvent, DataCodecPort, ResolvedSource } from '@/contract/index';
import type { AtomicFileSystemPort } from '../src/platform/file-writer.types';
import { FileSystemCache, MemoryCache } from '../src/platform/cache';
import { CodepotCancellationController } from '../src/platform/cancellation';
import { NodeCommandRunner } from '../src/platform/command-runner';
import { YamlJsonCodec } from '../src/platform/data-codec';
import { SequentialEventBus } from '../src/platform/event-bus';
import { ChangedAwareFileWriter } from '../src/platform/file-writer';
import { Sha256Hash } from '../src/platform/hash';
import { MemoryCommandRunner } from '../src/platform/memory-command-runner';
import { MemoryFileSystem } from '../src/platform/memory-file-system';
import { MemoryModuleLoader } from '../src/platform/memory-module-loader';
import { TsxModuleLoader } from '../src/platform/module-loader';
import { NodeFileSystem } from '../src/platform/node-file-system';
import { DefaultSourceResolver, MemorySourceRegistry } from '../src/platform/source-resolver';
import { FixedClock, SequentialIdProvider } from '../src/platform/system';

class JsonTestCodec implements DataCodecPort {
  parseJson<T>(text: string): T {
    return JSON.parse(text) as T;
  }

  stringifyJson(value: unknown): string {
    return `${JSON.stringify(value)}\n`;
  }

  parseYaml<T>(text: string): T {
    return JSON.parse(text) as T;
  }

  stringifyYaml(value: unknown): string {
    return `${JSON.stringify(value)}\n`;
  }
}

function event(sequence: number): CodepotEvent {
  return {
    version: 1,
    id: `event_${sequence}`,
    runId: 'run_1',
    sequence,
    timestamp: '2026-01-01T00:00:00.000Z',
    source: 'runtime',
    type: 'runtime.stage',
    payload: { stage: 'test', message: 'test' },
  };
}

async function verifyFileSystem(files: AtomicFileSystemPort, root: string): Promise<void> {
  const original = join(root, 'nested', 'file.txt');
  const moved = join(root, 'nested', 'moved.txt');
  await files.writeText(original, 'hello');
  assert.equal(await files.readText(original), 'hello');
  assert.equal((await files.stat(original)).kind, 'file');
  assert.deepEqual((await files.list(join(root, 'nested'))).map((entry) => entry.name), ['file.txt']);
  assert.deepEqual(await files.glob(['**/*.txt'], { cwd: root }), ['nested/file.txt']);
  await files.move(original, moved);
  assert.equal(await files.exists(original), false);
  assert.equal(await files.readText(moved), 'hello');
  await files.remove(join(root, 'nested'), { recursive: true });
  assert.equal(await files.exists(moved), false);
}

test('event bus preserves publish order and isolates listeners', async () => {
  const failures: string[] = [];
  const bus = new SequentialEventBus((error) => { failures.push(String(error)); });
  const received: string[] = [];
  bus.subscribe(async (current) => {
    received.push(`${current.sequence}:first`);
  });
  bus.subscribe(() => {
    throw new Error('observer failed');
  });
  bus.subscribe(async (current) => {
    received.push(`${current.sequence}:last`);
  });

  await Promise.all([bus.publish(event(1)), bus.publish(event(2))]);
  assert.deepEqual(received, ['1:first', '1:last', '2:first', '2:last']);
  assert.equal(failures.length, 2);
});

test('memory and node filesystem adapters share core behavior', async () => {
  const memory = new MemoryFileSystem(new FixedClock('2026-01-01T00:00:00.000Z'));
  await memory.mkdir('/project', { recursive: true });
  await verifyFileSystem(memory, '/project');

  const root = await mkdtemp(join(tmpdir(), 'codepot-fs-'));
  try {
    await verifyFileSystem(new NodeFileSystem(), root);
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});

test('changed-aware writer handles managed, immutable, raw, and layout-insensitive files', async () => {
  const files = new MemoryFileSystem(new FixedClock('2026-01-01T00:00:00.000Z'));
  const writer = new ChangedAwareFileWriter(files, new Sha256Hash(), new SequentialIdProvider());
  const path = '/output/model.ts';

  assert.equal((await writer.write({
    path,
    content: { encoding: 'utf8', text: 'export const value = 1;' },
    compareMode: 'exact',
    lifecycle: 'managed',
    atomic: true,
  })).status, 'created');

  assert.equal((await writer.write({
    path,
    content: { encoding: 'utf8', text: 'export const value = 1;' },
    compareMode: 'exact',
    lifecycle: 'managed',
    atomic: true,
  })).status, 'unchanged');

  assert.equal((await writer.write({
    path,
    content: { encoding: 'utf8', text: 'export const value = 2;' },
    compareMode: 'exact',
    lifecycle: 'immutable',
    atomic: true,
  })).status, 'refused');

  assert.equal((await writer.write({
    path: '/output/layout.ts',
    content: { encoding: 'utf8', text: 'export const value = 1;\n' },
    compareMode: 'layoutInsensitive',
    lifecycle: 'managed',
    atomic: true,
  })).status, 'created');

  assert.equal((await writer.write({
    path: '/output/layout.ts',
    content: { encoding: 'utf8', text: 'export   const value = 1;' },
    compareMode: 'layoutInsensitive',
    lifecycle: 'managed',
    atomic: true,
  })).status, 'unchanged');

  assert.equal((await writer.write({
    path: '/output/raw.bin',
    content: { encoding: 'base64', data: Buffer.from([1, 2, 3]).toString('base64') },
    compareMode: 'raw',
    lifecycle: 'managed',
    atomic: true,
  })).status, 'created');
});

test('memory cache expires entries deterministically', async () => {
  const clock = new FixedClock('2026-01-01T00:00:00.000Z');
  const cache = new MemoryCache(clock);
  await cache.set('key', { value: 1 }, 1_000);
  assert.deepEqual(await cache.get('key'), { value: 1 });
  clock.advance(1_001);
  assert.equal(await cache.get('key'), undefined);
});

test('command adapters support dry run, output capture, and cancellation', async () => {
  const runner = new NodeCommandRunner();
  const dry = await runner.run({ command: 'ignored', cwd: process.cwd(), environment: {}, dryRun: true });
  assert.equal(dry.skipped, true);

  const output = await runner.run({
    command: `${JSON.stringify(process.execPath)} -e "process.stdout.write('out'); process.stderr.write('err')"`,
    cwd: process.cwd(),
    environment: {},
  });
  assert.equal(output.exitCode, 0);
  assert.equal(output.stdout, 'out');
  assert.equal(output.stderr, 'err');

  const controller = new CodepotCancellationController();
  controller.cancel('test');
  const cancelled = await runner.run({
    command: `${JSON.stringify(process.execPath)} -e "setTimeout(() => {}, 1000)"`,
    cwd: process.cwd(),
    environment: {},
    signal: controller.signal,
  });
  assert.equal(cancelled.cancelled, true);
});

test('memory test adapters record commands and modules', async () => {
  const commands = new MemoryCommandRunner();
  const outcome = await commands.run({ command: 'echo test', cwd: '/project', environment: {} });
  assert.equal(outcome.exitCode, 0);
  assert.equal(commands.requests.length, 1);

  const modules = new MemoryModuleLoader();
  modules.register('/project/codepotx.config.ts', { value: 42 });
  assert.deepEqual(await modules.load('/project/codepotx.config.ts'), { value: 42 });
  assert.equal(modules.requests.length, 1);
});

test('memory source registry stores stable resolved sources', async () => {
  const registry = new MemorySourceRegistry();
  const source: ResolvedSource = {
    id: 'source:test',
    descriptor: { kind: 'memory', id: 'test' },
    root: '/project',
    entry: '/project/index.ts',
    digest: 'digest',
    files: [],
  };
  registry.register(source);
  assert.deepEqual(registry.get('test'), source);
});

test('data codec and hashing produce JSON-safe deterministic values', async () => {
  const codec = new YamlJsonCodec();
  const value = { z: 1, a: ['x'] };
  assert.deepEqual(codec.parseYaml(codec.stringifyYaml(value)), value);
  assert.deepEqual(codec.parseJson(codec.stringifyJson(value)), value);
  const hash = new Sha256Hash();
  assert.equal(await hash.text('same'), await hash.text('same'));
  assert.equal(await hash.values(['a', 'b']), await hash.values(['a', 'b']));
});

test('filesystem cache persists encoded payloads through the filesystem port', async () => {
  const files = new MemoryFileSystem(new FixedClock('2026-01-01T00:00:00.000Z'));
  const cache = new FileSystemCache(files, new JsonTestCodec(), '/cache');
  await cache.set('key/with/slashes', { value: 1 });
  assert.deepEqual(await cache.get('key/with/slashes'), { value: 1 });
  await cache.remove('key/with/slashes');
  assert.equal(await cache.get('key/with/slashes'), undefined);
});

test('module loader tracks the reachable entry and supports caching', async () => {
  const root = await mkdtemp(join(tmpdir(), 'codepot-module-'));
  try {
    const entry = join(root, 'config.ts');
    await new NodeFileSystem().writeText(entry, 'export default { value: 42 };\n');
    const loader = new TsxModuleLoader();
    const first = await loader.load<{ default: { value: number } }>(entry);
    const second = await loader.load<{ default: { value: number } }>(entry);
    assert.equal(first.default.value, 42);
    assert.equal(second.default.value, 42);
    assert.equal(first, second);
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});

test('source resolver handles local, package, git, artifact, and memory sources', async () => {
  const root = await mkdtemp(join(tmpdir(), 'codepot-source-'));
  try {
    const files = new NodeFileSystem();
    const codec = new YamlJsonCodec();
    const hash = new Sha256Hash();
    const modules = new TsxModuleLoader();
    const memory = new MemorySourceRegistry();
    const resolver = new DefaultSourceResolver({ files, codec, hash, modules, memory });

    await files.writeText(join(root, 'local', 'index.ts'), 'export default {};\n');
    const local = await resolver.resolve({ kind: 'local', path: 'local', entry: 'index.ts' }, { projectRoot: root });
    assert.equal(local.entry.endsWith('index.ts'), true);

    memory.register({
      id: 'memory:test',
      descriptor: { kind: 'memory', id: 'test' },
      root: '/memory',
      entry: '/memory/index.ts',
      digest: 'memory',
      files: [],
    });
    assert.equal((await resolver.resolve({ kind: 'memory', id: 'test' })).id, 'memory:test');
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});
