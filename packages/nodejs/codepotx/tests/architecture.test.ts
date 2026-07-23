import assert from 'node:assert/strict';
import { readFile, readdir } from 'node:fs/promises';
import { builtinModules } from 'node:module';
import { dirname, relative, resolve, sep } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const testsRoot = dirname(fileURLToPath(import.meta.url));
const packageRoot = resolve(testsRoot, '..');
const workspaceRoot = resolve(packageRoot, '../../..');
const sourceRoot = resolve(packageRoot, 'src');

const layers = [
  'contract',
  'authoring',
  'templating',
  'generation',
  'platform',
  'runtime',
  'internal',
] as const;

type Layer = (typeof layers)[number];

const allowedDependencies: Readonly<Record<Layer, ReadonlySet<Layer>>> = {
  contract: new Set(['contract']),
  authoring: new Set(['authoring', 'contract', 'internal']),
  templating: new Set(['templating', 'contract', 'internal']),
  generation: new Set(['generation', 'contract', 'internal']),
  platform: new Set(['platform', 'contract', 'internal']),
  runtime: new Set([
    'runtime',
    'contract',
    'authoring',
    'templating',
    'generation',
    'platform',
    'internal',
  ]),
  internal: new Set(['internal', 'contract']),
};

const domainLayers = new Set<Layer>([
  'contract',
  'authoring',
  'templating',
  'generation',
]);

const builtins = new Set([
  ...builtinModules,
  ...builtinModules.map((name) => `node:${name}`),
]);

interface ImportRecord {
  readonly file: string;
  readonly layer: Layer;
  readonly specifier: string;
  readonly targetLayer?: Layer;
}

interface ArchitectureViolation {
  readonly file: string;
  readonly message: string;
}

async function sourceFiles(root: string): Promise<readonly string[]> {
  const output: string[] = [];
  for (const entry of await readdir(root, { withFileTypes: true })) {
    const path = resolve(root, entry.name);
    if (entry.isDirectory()) output.push(...await sourceFiles(path));
    else if (entry.isFile() && entry.name.endsWith('.ts')) output.push(path);
  }
  return output.sort();
}

function isLayer(value: string): value is Layer {
  return layers.includes(value as Layer);
}

function layerForFile(file: string): Layer | undefined {
  const first = relative(sourceRoot, file).split(sep)[0];
  return first && isLayer(first) ? first : undefined;
}

function targetLayerForImport(file: string, specifier: string): Layer | undefined {
  if (specifier.startsWith('@/')) {
    const first = specifier.slice(2).split('/')[0];
    return first && isLayer(first) ? first : undefined;
  }
  if (!specifier.startsWith('.')) return undefined;
  const target = resolve(dirname(file), specifier);
  const first = relative(sourceRoot, target).split(sep)[0];
  return first && isLayer(first) ? first : undefined;
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

function inspectSource(file: string, source: string): readonly ArchitectureViolation[] {
  const layer = layerForFile(file);
  if (!layer) return [];
  const violations: ArchitectureViolation[] = [];

  for (const specifier of importSpecifiers(source)) {
    const targetLayer = targetLayerForImport(file, specifier);
    const record: ImportRecord = {
      file,
      layer,
      specifier,
      ...(targetLayer ? { targetLayer } : {}),
    };

    if (record.targetLayer && !allowedDependencies[layer].has(record.targetLayer)) {
      violations.push({
        file,
        message: `${layer} cannot import ${record.targetLayer}: ${specifier}`,
      });
    }
    if (domainLayers.has(layer) && builtins.has(specifier)) {
      violations.push({
        file,
        message: `${layer} cannot import Node built-in ${specifier}`,
      });
    }
    if (
      specifier.includes('codepotx-old')
      || specifier.includes('packages/python')
      || specifier.includes('codepotg/src')
    ) {
      violations.push({
        file,
        message: `active CodepotX source cannot import historical runtime source: ${specifier}`,
      });
    }
  }

  if (source.includes('@ts-ignore')) {
    violations.push({ file, message: '@ts-ignore is forbidden in active CodepotX source' });
  }
  const unsafeAnyPatterns = [
    /\bas\s+any\b/,
    /:\s*any(?:\[\])?(?=\s*[,;)=]|$)/m,
    /<\s*any\s*>/,
    /\bany\[\]/,
  ];
  if (unsafeAnyPatterns.some((pattern) => pattern.test(source))) {
    violations.push({ file, message: 'explicit any is forbidden in active CodepotX source' });
  }

  return violations;
}

function assertAcyclic(graph: ReadonlyMap<Layer, ReadonlySet<Layer>>): void {
  const visiting = new Set<Layer>();
  const visited = new Set<Layer>();

  const visit = (layer: Layer, trail: readonly Layer[]): void => {
    if (visited.has(layer)) return;
    assert.equal(
      visiting.has(layer),
      false,
      `cross-layer dependency cycle: ${[...trail, layer].join(' -> ')}`,
    );
    visiting.add(layer);
    for (const dependency of graph.get(layer) ?? []) {
      if (dependency !== layer) visit(dependency, [...trail, layer]);
    }
    visiting.delete(layer);
    visited.add(layer);
  };

  for (const layer of graph.keys()) visit(layer, []);
}

test('active source follows the approved dependency and type-safety boundaries', async () => {
  const violations: ArchitectureViolation[] = [];
  const graph = new Map<Layer, Set<Layer>>();

  for (const file of await sourceFiles(sourceRoot)) {
    const source = await readFile(file, 'utf8');
    const layer = layerForFile(file);
    if (!layer) continue;
    violations.push(...inspectSource(file, source));
    const dependencies = graph.get(layer) ?? new Set<Layer>();
    for (const specifier of importSpecifiers(source)) {
      const targetLayer = targetLayerForImport(file, specifier);
      if (targetLayer) dependencies.add(targetLayer);
    }
    graph.set(layer, dependencies);
  }

  assert.deepEqual(violations, []);
  assertAcyclic(graph);
});

test('architecture scanner rejects a known forbidden dependency fixture', () => {
  const fixture = resolve(sourceRoot, 'authoring/forbidden-fixture.ts');
  const violations = inspectSource(
    fixture,
    "import { createGenerationEngine } from '@/generation/index';\nvoid createGenerationEngine;\n",
  );
  assert.equal(violations.length, 1);
  assert.match(violations[0]?.message ?? '', /authoring cannot import generation/);
});

test('public package subpaths and build entrypoints remain stable', async () => {
  const packageJson = JSON.parse(
    await readFile(resolve(packageRoot, 'package.json'), 'utf8'),
  ) as {
    readonly version: string;
    readonly exports: Readonly<Record<string, unknown>>;
  };
  assert.equal(packageJson.version, '0.0.0');
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

  const buildConfig = await readFile(resolve(packageRoot, 'tsdown.config.ts'), 'utf8');
  for (const entry of [
    'src/index.ts',
    'src/contract/index.ts',
    'src/runtime/index.ts',
    'src/platform/index.ts',
    'src/authoring/index.ts',
    'src/templating/index.ts',
    'src/generation/index.ts',
  ]) {
    assert.match(buildConfig, new RegExp(`['\"]${entry.replaceAll('/', '\\/')}['\"]`));
  }
});

test('workspace strict compiler safeguards remain enabled', async () => {
  const config = JSON.parse(
    await readFile(resolve(workspaceRoot, 'tsconfig.base.json'), 'utf8'),
  ) as { readonly compilerOptions: Readonly<Record<string, unknown>> };
  const required = {
    strict: true,
    isolatedModules: true,
    isolatedDeclarations: true,
    exactOptionalPropertyTypes: true,
    noUncheckedIndexedAccess: true,
    noImplicitReturns: true,
    useUnknownInCatchVariables: true,
  } as const;
  for (const [name, expected] of Object.entries(required)) {
    assert.equal(config.compilerOptions[name], expected, `${name} must remain enabled`);
  }
});
