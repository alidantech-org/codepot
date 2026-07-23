import assert from 'node:assert/strict';
import { readFile, readdir, stat } from 'node:fs/promises';
import { dirname, relative, resolve, sep } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const testsRoot = dirname(fileURLToPath(import.meta.url));
const contractRoot = resolve(testsRoot, '../src/contract');

async function typescriptFiles(root: string): Promise<readonly string[]> {
  const output: string[] = [];
  for (const entry of await readdir(root, { withFileTypes: true })) {
    const path = resolve(root, entry.name);
    if (entry.isDirectory()) output.push(...await typescriptFiles(path));
    else if (entry.isFile() && entry.name.endsWith('.ts')) output.push(path);
  }
  return output.sort();
}

function importSpecifiers(source: string): readonly string[] {
  const output: string[] = [];
  const staticPattern = /(?:import|export)\s+(?:type\s+)?(?:[^'";]*?\s+from\s+)?['"]([^'"]+)['"]/g;
  const dynamicPattern = /import\(\s*['"]([^'"]+)['"]\s*\)/g;
  for (const match of source.matchAll(staticPattern)) {
    if (match[1]) output.push(match[1]);
  }
  for (const match of source.matchAll(dynamicPattern)) {
    if (match[1]) output.push(match[1]);
  }
  return output;
}

async function isFile(path: string): Promise<boolean> {
  try {
    return (await stat(path)).isFile();
  } catch {
    return false;
  }
}

async function resolveContractImport(file: string, specifier: string): Promise<string | undefined> {
  if (!specifier.startsWith('.')) return undefined;
  const base = resolve(dirname(file), specifier);
  for (const candidate of [`${base}.ts`, resolve(base, 'index.ts'), base]) {
    if (await isFile(candidate)) return candidate;
  }
  return undefined;
}

function display(path: string): string {
  return relative(contractRoot, path).split(sep).join('/');
}

function assertAcyclic(graph: ReadonlyMap<string, ReadonlySet<string>>): void {
  const visiting = new Set<string>();
  const visited = new Set<string>();

  const visit = (file: string, trail: readonly string[]): void => {
    if (visited.has(file)) return;
    assert.equal(
      visiting.has(file),
      false,
      `contract import cycle: ${[...trail, file].map(display).join(' -> ')}`,
    );
    visiting.add(file);
    for (const dependency of graph.get(file) ?? []) {
      visit(dependency, [...trail, file]);
    }
    visiting.delete(file);
    visited.add(file);
  };

  for (const file of graph.keys()) visit(file, []);
}

test('contract ownership tree has no external, implementation, or circular imports', async () => {
  const graph = new Map<string, Set<string>>();
  for (const file of await typescriptFiles(contractRoot)) {
    const source = await readFile(file, 'utf8');
    const dependencies = new Set<string>();
    for (const specifier of importSpecifiers(source)) {
      assert.equal(
        specifier.startsWith('.'),
        true,
        `${display(file)} imports non-contract module ${specifier}`,
      );
      const target = await resolveContractImport(file, specifier);
      assert.ok(target, `${display(file)} has unresolved import ${specifier}`);
      assert.equal(
        relative(contractRoot, target).startsWith('..'),
        false,
        `${display(file)} escapes contract ownership through ${specifier}`,
      );
      dependencies.add(target);
    }
    graph.set(file, dependencies);
  }
  assertAcyclic(graph);
});

test('contract facade and compatibility shims point at owned modules', async () => {
  const facade = await readFile(resolve(contractRoot, 'index.ts'), 'utf8');
  for (const owner of [
    './protocol/index',
    './sources/index',
    './diagnostics/index',
    './artifacts/index',
    './operations/index',
    './events/index',
    './ports/index',
  ]) {
    assert.match(facade, new RegExp(owner.replaceAll('/', '\\/')));
  }

  const shims: Readonly<Record<string, string>> = {
    'artifact.types.ts': './protocol/artifact.types',
    'common.types.ts': './protocol/common.types',
    'sources.types.ts': './sources/index',
    'diagnostics.types.ts': './diagnostics/index',
    'authoring-artifact.types.ts': './artifacts/authoring/index',
    'template-artifact.types.ts': './artifacts/templating/template-pack.types',
    'template-variables.types.ts': './artifacts/templating/template-variables.types',
    'generation-artifact.types.ts': './artifacts/generation/index',
    'events.types.ts': './events/index',
    'requests.types.ts': './operations/',
    'runtime.types.ts': './operations/runtime/index',
    'ports.types.ts': './ports/index',
    'template-introspection.types.ts': './ports/engines/template-introspection.types',
  };
  for (const [path, target] of Object.entries(shims)) {
    const source = await readFile(resolve(contractRoot, path), 'utf8');
    assert.match(source, new RegExp(target.replaceAll('/', '\\/')));
  }
});
