import assert from 'node:assert/strict';
import { readFile, readdir } from 'node:fs/promises';
import { dirname, relative, resolve } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const testsRoot = dirname(fileURLToPath(import.meta.url));
const packageRoot = resolve(testsRoot, '..');
const workspaceRoot = resolve(packageRoot, '../../..');
const sourceRoot = resolve(packageRoot, 'src');

async function text(path: string): Promise<string> {
  return readFile(path, 'utf8');
}

async function source(path: string): Promise<string> {
  return text(resolve(sourceRoot, path));
}

async function files(root: string): Promise<readonly string[]> {
  const output: string[] = [];
  for (const entry of await readdir(root, { withFileTypes: true })) {
    const path = resolve(root, entry.name);
    if (entry.isDirectory()) output.push(...await files(path));
    else if (entry.isFile()) output.push(path);
  }
  return output.sort();
}

test('final facades remain orchestration-sized', async () => {
  const maximumLines: Readonly<Record<string, number>> = {
    'authoring/compiler/authoring-compiler.ts': 170,
    'authoring/engine/authoring-engine.ts': 80,
    'templating/templating-engine.ts': 100,
    'generation/generation-engine.ts': 100,
    'runtime/runtime.ts': 140,
    'platform/create-platform-services.ts': 120,
  };
  for (const [path, maximum] of Object.entries(maximumLines)) {
    const count = (await source(path)).split('\n').length;
    assert.ok(count <= maximum, `${path} has ${count} lines; maximum is ${maximum}`);
  }
});

test('grouped runner reaches every original behavior suite exactly once', async () => {
  const groupFiles = [
    'tests/architecture/index.test.ts',
    'tests/compatibility/index.test.ts',
    'tests/contract/index.test.ts',
    'tests/unit/authoring/index.test.ts',
    'tests/unit/generation/index.test.ts',
    'tests/unit/platform/index.test.ts',
    'tests/unit/runtime/index.test.ts',
    'tests/unit/templating/index.test.ts',
    'tests/integration/index.test.ts',
  ];
  const references = new Map<string, number>();
  for (const path of groupFiles) {
    const value = await text(resolve(packageRoot, path));
    for (const match of value.matchAll(/import\s+['"]([^'"]+\.test)['"]/g)) {
      const imported = match[1];
      if (!imported) continue;
      const name = imported.split('/').at(-1);
      if (!name) continue;
      references.set(name, (references.get(name) ?? 0) + 1);
    }
  }
  const expected = [
    'architecture.test',
    'authoring-compatibility.test',
    'authoring-refs-properties.test',
    'authoring-schema.test',
    'baseline.test',
    'contract-partitioning.test',
    'default-runtime.test',
    'generation-determinism.test',
    'generation-hardening.test',
    'generation.test',
    'platform.test',
    'public-exports.test',
    'runtime-platform-modularization.test',
    'runtime.test',
    'structure-integration.test',
    'structural-modularization.test',
    'template-variables.test',
    'templating.test',
  ].sort();
  assert.deepEqual([...references.keys()].sort(), expected);
  for (const [name, count] of references) assert.equal(count, 1, `${name} is imported ${count} times`);
});

test('public entrypoints and package scripts match the documented boundary', async () => {
  const packageJson = JSON.parse(await text(resolve(packageRoot, 'package.json'))) as {
    readonly exports: Readonly<Record<string, unknown>>;
    readonly scripts: Readonly<Record<string, string>>;
  };
  assert.deepEqual(Object.keys(packageJson.exports), [
    '.',
    './contract',
    './runtime',
    './platform',
    './authoring',
    './templating',
    './generation',
    './package.json',
  ]);
  for (const name of [
    'test:architecture',
    'test:compatibility',
    'test:contract',
    'test:unit:authoring',
    'test:unit:templating',
    'test:unit:generation',
    'test:unit:runtime',
    'test:unit:platform',
    'test:integration',
  ]) {
    assert.ok(packageJson.scripts[name], `missing script ${name}`);
  }
  for (const path of [
    'index.ts',
    'contract/index.ts',
    'runtime/index.ts',
    'platform/index.ts',
    'authoring/index.ts',
    'templating/index.ts',
    'generation/index.ts',
  ]) {
    const value = await source(path);
    assert.doesNotMatch(value, /export\s+(?:type\s+)?\*/u);
    assert.doesNotMatch(value, /from ['"].*\/(?:application|passes|dispatch)\//u);
  }
});

test('owned source does not depend on moved platform compatibility shims', async () => {
  const shimNames = [
    'cache',
    'command-runner',
    'data-codec',
    'event-bus',
    'file-writer',
    'hash',
    'memory-command-runner',
    'memory-file-system',
    'memory-module-loader',
    'module-loader',
    'node-file-system',
    'source-resolver',
    'system',
  ];
  const shims = new Set([
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
    'platform/system.ts',
  ]);
  const violations: string[] = [];
  for (const path of await files(resolve(sourceRoot, 'platform'))) {
    if (!path.endsWith('.ts')) continue;
    const relativePath = relative(sourceRoot, path).replaceAll('\\', '/');
    if (shims.has(relativePath)) continue;
    const value = await text(path);
    const fromRoot = relativePath.split('/').length > 2 ? '../' : './';
    for (const name of shimNames) {
      const specifier = `${fromRoot}${name}`;
      if (value.includes(`from '${specifier}'`) || value.includes(`from "${specifier}"`)) {
        violations.push(`${relativePath}: ${specifier}`);
      }
    }
  }
  assert.deepEqual(violations, []);
});

test('migration documentation and task records are complete or at final gate', async () => {
  const readme = await text(resolve(packageRoot, 'README.md'));
  const architecture = await text(resolve(workspaceRoot, 'agents/ARCHITECTURE.md'));
  const audit = await text(resolve(workspaceRoot, 'agents/audits/CODEPOTX_STRUCTURE_FINAL.md'));
  for (const phrase of [
    'Add an authoring compiler pass',
    'Add a template capability',
    'Add a generation stage',
    'Add a runtime operation',
    'Add a platform adapter',
  ]) assert.match(readme, new RegExp(phrase));
  assert.match(architecture, /RuntimeOperationHandlerRegistry/);
  assert.match(audit, /Tasks 15–23/);

  for (const task of [16, 17, 18, 19, 20]) {
    const matches = (await text(resolve(
      workspaceRoot,
      `agents/tasks/${String(task).padStart(2, '0')}-codepotx-${task === 16 ? 'architecture-guardrails' : task === 17 ? 'contract-restructure' : task === 18 ? 'authoring-restructure' : task === 19 ? 'templating-restructure' : 'generation-restructure'}.md`,
    ))).match(/^Status:\s+\[x\]/m);
    assert.ok(matches, `Task ${task} must be complete`);
  }
  for (const [task, file] of [
    [21, '21-codepotx-runtime-platform-restructure.md'],
    [22, '22-codepotx-tests-exports-cleanup.md'],
    [23, '23-codepotx-structure-integration-gate.md'],
  ] as const) {
    const value = await text(resolve(workspaceRoot, `agents/tasks/${file}`));
    assert.match(value, /^Status:\s+\[(?:~|x)\]/m, `Task ${task} must be active or complete`);
  }
});
