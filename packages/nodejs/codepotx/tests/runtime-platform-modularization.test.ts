import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const testsRoot = dirname(fileURLToPath(import.meta.url));
const sourceRoot = resolve(testsRoot, '../src');

async function source(path: string): Promise<string> {
  return readFile(resolve(sourceRoot, path), 'utf8');
}

test('runtime dispatch is exhaustive and contains no central unsafe switch', async () => {
  const runtime = await source('runtime/runtime.ts');
  const operationMap = await source('contract/operations/runtime/index.ts');
  const handlers = await source('runtime/dispatch/create-runtime-handlers.ts');
  assert.doesNotMatch(runtime, /switch\s*\(\s*request\.kind\s*\)/);
  assert.doesNotMatch(runtime, /\bas\s+never\b/);
  assert.match(runtime, /dispatchRuntimeOperation/);

  const operationKinds = [...operationMap.matchAll(/readonly\s+'([^']+)'\s*:/g)]
    .map((match) => match[1])
    .filter((value): value is string => value !== undefined)
    .sort();
  const handlerKinds = [...handlers.matchAll(/^\s*'([^']+)'\s*:/gm)]
    .map((match) => match[1])
    .filter((value): value is string => value !== undefined)
    .sort();
  assert.deepEqual(handlerKinds, operationKinds);
  assert.match(handlers, /satisfies\s+RuntimeOperationHandlerRegistry/);
});

test('runtime context and composition have explicit ownership', async () => {
  for (const path of [
    'runtime/context/create-run-context.ts',
    'runtime/context/run-context-store.ts',
    'runtime/dispatch/runtime-handler.types.ts',
    'runtime/dispatch/dispatch-runtime-operation.ts',
    'runtime/composition/default-features.ts',
    'runtime/composition/default-runtime.ts',
  ]) {
    assert.ok((await source(path)).trim().length > 0, `${path} must exist`);
  }
  assert.ok((await source('runtime/run-context.ts')).split('\n').length <= 3);
  assert.ok((await source('runtime/default-runtime.ts')).split('\n').length <= 6);
});

test('platform composition uses node memory and shared capability folders', async () => {
  const composition = await source('platform/create-platform-services.ts');
  assert.match(composition, /from '\.\/node\/index'/);
  assert.match(composition, /from '\.\/memory\/index'/);
  assert.match(composition, /from '\.\/shared\/index'/);

  for (const path of [
    'platform/node/file-system.ts',
    'platform/node/command-runner.ts',
    'platform/node/module-loader.ts',
    'platform/node/file-system-cache.ts',
    'platform/node/source-resolver.ts',
    'platform/memory/file-system.ts',
    'platform/memory/command-runner.ts',
    'platform/memory/module-loader.ts',
    'platform/memory/cache.ts',
    'platform/memory/source-store.ts',
    'platform/shared/cancellation.ts',
    'platform/shared/data-codec.ts',
    'platform/shared/event-bus.ts',
    'platform/shared/file-writer.ts',
    'platform/shared/hash.ts',
    'platform/shared/source-resolver.types.ts',
    'platform/shared/system.ts',
  ]) {
    assert.ok((await source(path)).trim().length > 0, `${path} must exist`);
  }
});

test('moved flat platform files are compatibility shims only', async () => {
  for (const path of [
    'platform/cache.ts',
    'platform/command-runner.ts',
    'platform/data-codec.ts',
    'platform/event-bus.ts',
    'platform/file-writer.ts',
    'platform/hash.ts',
    'platform/memory-command-runner.ts',
    'platform/memory-file-system.ts',
    'platform/memory-module-loader.ts',
    'platform/module-loader.ts',
    'platform/node-file-system.ts',
    'platform/source-resolver.ts',
    'platform/source-resolver.types.ts',
  ]) {
    const value = await source(path);
    assert.ok(value.split('\n').length <= 6, `${path} must remain a thin shim`);
  }
});
