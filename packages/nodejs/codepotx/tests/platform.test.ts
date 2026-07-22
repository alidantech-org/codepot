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
  assert.deepEqual(await files.glob(['**/*.txt'], { cwd: root }), [join('nested', 'file.txt')]);
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
    content: { encoding: 'utf8', text: 'export const value = 1;\n\n' },
    compareMode: 'exact',
    lifecycle: 'managed',
  })).status, 'unchanged');
  assert.equal((await writer.write({
    path,
    content: { encoding: 'utf8', text: 'export   const value=1;' },
    compareMode: 'layoutInsensitive',
    lifecycle: 'managed',
  })).status, 'unchanged');
  assert.equal((await writer.write({
    path,
    content: { encoding: 'utf8', text: 'changed' },
    compareMode: 'raw',
    lifecycle: 'immutable',
  })).status, 'skipped');
  assert.equal(await files.readText(path), 'export const value = 1;\n');
});

test('memory cache expires entries deterministically', async () => {
  const clock = new FixedClock('2026-01-01T00:00:00.000Z');
  const cache = new MemoryCache(clock);
  await cache.set({
    key: 'authoring:one',
    value: { encoding: 'utf8', data: '{}' },
    createdAt: clock.now(),
    expiresAt: '2026-01-01T00:00:01.000Z',
  });
  assert.equal((await cache.get('authoring:one'))?.key, 'authoring:one');
  clock.advance(1_001);
  assert.equal(await cache.get('authoring:one'), null);
});

test('command adapters support dry run, output capture, and cancellation', async () => {
  const runner = new NodeCommandRunner();
  const dry = await runner.run({
    command: 'not-executed',
    cwd: process.cwd(),
    environment: {},
    dryRun: true,
  });
  assert.equal(dry.skipped, true);

  const completed = await runner.run({
    command: `${process.execPath} -e "process.stdout.write(process.env.CODEPOT_VALUE)"`,
    cwd: process.cwd(),
    environment: { CODEPOT_VALUE: 'captured' },
  });
  assert.equal(completed.exitCode, 0);
  assert.equal(completed.stdout, 'captured');

  const controller = new CodepotCancellationController();
  const pending = runner.run({
    command: `${process.execPath} -e "setTimeout(() => {}, 5000)"`,
    cwd: process.cwd(),
    environment: {},
    signal: controller.signal,
  });
  setTimeout(() => controller.abort('test cancellation'), 20);
  await assert.rejects(pending, /test cancellation/u);
});

test('memory test adapters record commands and modules', async () => {
  const commands = new MemoryCommandRunner();
  await commands.run({ command: 'format', cwd: '/project', environment: {} });
  assert.equal(commands.requests.length, 1);

  const modules = new MemoryModuleLoader();
  modules.register('/project/codepotx.config.ts', { default: { contracts: [] } });
  const loaded = await modules.load<{ readonly default: object }>('/project/codepotx.config.ts');
  assert.deepEqual(loaded.exports.default, { contracts: [] });
});

test('memory source registry stores stable resolved sources', () => {
  const registry = new MemorySourceRegistry();
  const source: ResolvedSource = {
    id: 'source_1',
    descriptor: { kind: 'memory', id: 'contracts' },
    root: '/contracts',
    entry: '/contracts/codepotx.config.ts',
    digest: 'digest',
    files: [],
  };
  registry.register(source);
  assert.deepEqual(registry.get('source_1'), source);
  assert.equal(registry.delete('source_1'), true);
});

test('data codec and hashing produce JSON-safe deterministic values', async () => {
  const codec = new YamlJsonCodec();
  assert.deepEqual(codec.parseYaml('name: codepot\ncount: 2\n'), { name: 'codepot', count: 2 });
  assert.equal(codec.stringifyJson({ value: 1 }, { pretty: true }).endsWith('\n'), true);
  assert.throws(() => codec.stringifyJson({ date: new Date() }), /Non-JSON object/u);

  const hash = new Sha256Hash();
  assert.equal(
    await hash.values([{ beta: 2, alpha: 1 }]),
    await hash.values([{ alpha: 1, beta: 2 }]),
  );
});

test('filesystem cache persists encoded payloads through the filesystem port', async () => {
  const clock = new FixedClock('2026-01-01T00:00:00.000Z');
  const files = new MemoryFileSystem(clock);
  const cache = new FileSystemCache('/cache', files, new JsonTestCodec(), new Sha256Hash(), clock);
  await cache.set({
    key: 'templates:pack',
    value: { encoding: 'utf8', data: '{"kind":"codepot.templates"}' },
    createdAt: clock.now(),
  });
  assert.equal((await cache.get('templates:pack'))?.value.encoding, 'utf8');
  assert.equal(await cache.delete('templates:pack'), true);
  assert.equal(await cache.get('templates:pack'), null);
});

test('module loader tracks the reachable entry and supports caching', async () => {
  const root = await mkdtemp(join(tmpdir(), 'codepot-module-'));
  try {
    const entry = join(root, 'config.mjs');
    const files = new NodeFileSystem();
    await files.writeText(entry, 'export default { name: "codepot" };\n');
    const loader = new TsxModuleLoader(files, new Sha256Hash());
    const first = await loader.load<{ readonly default: { readonly name: string } }>(entry, { cache: true });
    const second = await loader.load<{ readonly default: { readonly name: string } }>(entry, { cache: true });
    assert.equal(first.exports.default.name, 'codepot');
    assert.equal(first, second);
    assert.equal(first.files.some((file) => file.path === entry), true);
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});

test('source resolver handles local, package, git, artifact, and memory sources', async () => {
  const root = await mkdtemp(join(tmpdir(), 'codepot-sources-'));
  const files = new NodeFileSystem();
  const hash = new Sha256Hash();
  const codec = new JsonTestCodec();
  const commands = new NodeCommandRunner();
  const memory = new MemorySourceRegistry();
  const resolver = new DefaultSourceResolver(files, hash, codec, commands, {
    cacheRoot: join(root, '.sources'),
    memory,
  });

  try {
    const localRoot = join(root, 'local');
    await files.writeText(join(localRoot, 'codepotx.config.ts'), 'export default {};\n');
    const local = await resolver.resolve({ kind: 'local', path: localRoot, entry: 'codepotx.config.ts' });
    assert.equal(local.files.length, 1);

    const artifact = await resolver.resolve({ kind: 'artifact', path: join(localRoot, 'codepotx.config.ts') });
    assert.equal(artifact.entry.endsWith('codepotx.config.ts'), true);

    const packageRoot = join(root, 'node_modules', 'test-codepot-source');
    await files.writeText(join(packageRoot, 'package.json'), JSON.stringify({
      name: 'test-codepot-source',
      version: '1.0.0',
      main: 'index.js',
    }));
    await files.writeText(join(packageRoot, 'index.js'), 'module.exports = {};\n');
    const packaged = await resolver.resolve({
      kind: 'package',
      package: 'test-codepot-source',
      version: '1.0.0',
      entry: 'index.js',
    }, { projectRoot: root });
    assert.equal(packaged.root, packageRoot);

    const repository = join(root, 'repository');
    await files.mkdir(repository, { recursive: true });
    for (const command of [
      'git init',
      'git config user.email "codepot@example.test"',
      'git config user.name "Codepot Test"',
    ]) {
      assert.equal((await commands.run({ command, cwd: repository, environment: {} })).exitCode, 0);
    }
    await files.writeText(join(repository, 'paths.yaml'), 'folders: {}\n');
    assert.equal((await commands.run({ command: 'git add . && git commit -m "initial"', cwd: repository, environment: {} })).exitCode, 0);
    const git = await resolver.resolve({ kind: 'git', repository, ref: 'HEAD', entry: 'paths.yaml' });
    assert.equal(git.entry.endsWith('paths.yaml'), true);

    const memorySource: ResolvedSource = {
      id: 'memory_source',
      descriptor: { kind: 'memory', id: 'contracts' },
      root: '/memory',
      entry: '/memory/codepotx.config.ts',
      digest: 'memory-digest',
      files: [],
    };
    memory.register(memorySource);
    assert.equal((await resolver.resolve({ kind: 'memory', id: 'memory_source' })).digest, 'memory-digest');
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});
