import assert from 'node:assert/strict';
import { access, readFile, readdir } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const testsRoot = dirname(fileURLToPath(import.meta.url));
const sourceRoot = resolve(testsRoot, '../src');

async function exists(path: string): Promise<boolean> {
  try {
    await access(path);
    return true;
  } catch {
    return false;
  }
}

async function typescriptFiles(root: string): Promise<readonly string[]> {
  const output: string[] = [];
  for (const entry of await readdir(root, { withFileTypes: true })) {
    const path = resolve(root, entry.name);
    if (entry.isDirectory()) output.push(...await typescriptFiles(path));
    else if (entry.isFile() && entry.name.endsWith('.ts')) output.push(path);
  }
  return output.sort();
}

async function lineCount(path: string): Promise<number> {
  return (await readFile(path, 'utf8')).split(/\r?\n/u).length;
}

test('authoring, templating, and generation expose focused module ownership', async () => {
  const required = [
    'authoring/application/compile-authoring.ts',
    'authoring/application/validate-authoring.ts',
    'authoring/application/inspect-authoring.ts',
    'authoring/application/load-authoring-artifact.ts',
    'authoring/application/cache-authoring.ts',
    'authoring/compiler/authoring-compiler.ts',
    'authoring/compiler/compiler-context.ts',
    'authoring/compiler/passes/compile-resources.ts',
    'authoring/compiler/schema/schema-normalizer.ts',
    'authoring/compiler/validation/validate-operations.ts',
    'templating/config/normalized-paths-config.ts',
    'templating/compiler/discover-template-files.ts',
    'templating/compiler/compile-template-descriptors.ts',
    'templating/compiler/assemble-template-pack.ts',
    'templating/context/create-template-context.ts',
    'templating/rendering/render-template-files.ts',
    'templating/variables/list-template-variables.ts',
    'templating/variables/validate-template-context.ts',
    'generation/application/load-codepot-file.ts',
    'generation/application/plan-generation.ts',
    'generation/application/render-generation.ts',
    'generation/application/write-generation.ts',
    'generation/application/clean-generation.ts',
    'generation/application/run-generation-commands.ts',
    'generation/application/execute-generation.ts',
    'generation/planning/prepare-generation-plan.ts',
  ];
  for (const relative of required) {
    assert.equal(await exists(resolve(sourceRoot, relative)), true, relative);
  }
});

test('public engine classes remain small facades after modularization', async () => {
  const limits: Readonly<Record<string, number>> = {
    'authoring/compiler/compiler.ts': 10,
    'authoring/engine/authoring-engine.ts': 90,
    'templating/templating-engine.ts': 100,
    'generation/generation-engine.ts': 110,
  };
  for (const [relative, maximum] of Object.entries(limits)) {
    const count = await lineCount(resolve(sourceRoot, relative));
    assert.ok(count <= maximum, `${relative} has ${count} lines; maximum is ${maximum}`);
  }
});

test('artifact producers use the centralized package metadata source', async () => {
  const forbidden = "producer: { name: 'codepotx', version: '0.0.0' }";
  const offenders: string[] = [];
  for (const path of await typescriptFiles(sourceRoot)) {
    const source = await readFile(path, 'utf8');
    if (source.includes(forbidden)) offenders.push(path);
  }
  assert.deepEqual(offenders, []);
  const packageInfo = await readFile(
    resolve(sourceRoot, 'internal/package-info.ts'),
    'utf8',
  );
  assert.match(packageInfo, /CODEPOT_ARTIFACT_PRODUCER/u);
});
