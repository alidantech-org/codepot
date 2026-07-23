import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

import {
  DefaultAuthoringCompiler,
  defineCodepotConfig,
  defineVersionContract,
  z,
} from '../src/authoring/index';
import type {
  AuthoringPort,
  CompiledAuthoringArtifact,
  ResolvedSource,
} from '../src/contract/index';
import { createGenerationEngine } from '../src/generation/index';
import {
  createMemoryPlatformServices,
  Sha256Hash,
} from '../src/platform/index';
import {
  createTemplatingEngine,
  resolveOutputTokens,
} from '../src/templating/index';

const testsRoot = dirname(fileURLToPath(import.meta.url));
const packageRoot = resolve(testsRoot, '..');

interface BaselineSnapshot {
  readonly branch: string;
  readonly packageVersion: string;
  readonly authoring: {
    readonly artifactKind: string;
    readonly project: {
      readonly name: string;
      readonly version: string;
    };
    readonly operationIds: readonly string[];
    readonly cacheInvalidates: Readonly<Record<string, readonly string[]>>;
  };
  readonly templating: {
    readonly artifactKind: string;
    readonly packName: string;
    readonly templateCount: number;
    readonly outputPath: string;
    readonly renderedText: string;
  };
  readonly generation: {
    readonly task: string;
    readonly outputRoot: string;
    readonly plannedFiles: readonly string[];
    readonly clean: readonly {
      readonly path: string;
      readonly allowed: boolean;
    }[];
    readonly renderedFiles: readonly string[];
    readonly renderedText: string;
  };
}

function authoringSource(): ResolvedSource {
  return {
    id: 'source:baseline',
    descriptor: { kind: 'memory', id: 'baseline' },
    root: '/contracts',
    entry: '/contracts/codepotx.config.ts',
    digest: 'source-baseline',
    files: [],
  };
}

async function compileAuthoring(): Promise<CompiledAuthoringArtifact> {
  const version = defineVersionContract({
    info: { title: 'Structure Baseline', version: '1.0.0' },
  });
  const shared = version.defineProperties('Shared', {
    id: z.string(),
    name: z.string().min(1),
  });
  const schemas = version.defineSchemas({
    User: {
      id: shared.ref.id,
      name: shared.ref.name,
    },
  });
  const users = version.defineResource({
    name: 'users',
    route: '/v1/users',
    folders: ['platform', 'auth'],
  });
  users.defineRoutes().routes((route) => ({
    listUsers: route.get('/').response(schemas.ref.User.array()),
    updateUser: route.patch('/:id')
      .body(schemas.ref.User.partial())
      .response(schemas.ref.User)
      .cache((cache) => cache.invalidate.on('listUsers')),
  }));

  const compiler = new DefaultAuthoringCompiler({ hash: new Sha256Hash() });
  const output = await compiler.compile({
    config: defineCodepotConfig({ contracts: [version] }),
    source: authoringSource(),
  });
  assert.equal(
    output.diagnostics.some((item) => item.severity === 'error'),
    false,
  );
  return output.artifact;
}

function assertJsonSafe(value: unknown, path = '$'): void {
  if (value === null) return;
  if (
    typeof value === 'string'
    || typeof value === 'number'
    || typeof value === 'boolean'
  ) return;
  assert.notEqual(typeof value, 'undefined', `${path} contains undefined`);
  assert.notEqual(typeof value, 'function', `${path} contains a function`);
  assert.notEqual(typeof value, 'symbol', `${path} contains a symbol`);
  assert.notEqual(typeof value, 'bigint', `${path} contains a bigint`);
  if (Array.isArray(value)) {
    value.forEach((item, index) => assertJsonSafe(item, `${path}[${index}]`));
    return;
  }
  assert.equal(typeof value, 'object', `${path} must be JSON-compatible`);
  assert.equal(
    Object.getPrototypeOf(value),
    Object.prototype,
    `${path} contains a non-plain implementation instance`,
  );
  for (const [key, item] of Object.entries(value)) {
    assertJsonSafe(item, `${path}.${key}`);
  }
}

async function expectedBaseline(): Promise<BaselineSnapshot> {
  return JSON.parse(
    await readFile(
      resolve(testsRoot, 'fixtures/baseline/codepotx-structure-baseline.json'),
      'utf8',
    ),
  ) as BaselineSnapshot;
}

test('authoring, templating, and generation match the structural migration baseline', async () => {
  const baseline = await expectedBaseline();
  const packageJson = JSON.parse(
    await readFile(resolve(packageRoot, 'package.json'), 'utf8'),
  ) as { readonly version: string };
  assert.equal(baseline.branch, 'chatgpt/codepotx-restart');
  assert.equal(packageJson.version, baseline.packageVersion);

  const authoring = await compileAuthoring();
  const authoringAgain = await compileAuthoring();
  assert.deepEqual(authoringAgain, authoring);
  assertJsonSafe(authoring);
  assert.deepEqual(JSON.parse(JSON.stringify(authoring)), authoring);

  const authoringSummary = {
    artifactKind: authoring.header.kind,
    project: {
      name: authoring.project.name,
      version: authoring.project.version,
    },
    operationIds: authoring.operations.map((operation) => operation.operationId),
    cacheInvalidates: Object.fromEntries(
      authoring.operations.map((operation) => [
        operation.operationId,
        operation.cacheInvalidates,
      ]),
    ),
  };
  assert.deepEqual(authoringSummary, baseline.authoring);

  const platform = createMemoryPlatformServices();
  await platform.files.mkdir('/project/templates/{model}', { recursive: true });
  await platform.files.writeText('/project/templates/paths.yaml', `
name: baseline-pack
version: 1.0.0
helpers: [pascal]
folders:
  model:
    select: authoring.schemas
    as: model
    mode: each
    parts: [src, models]
write:
  clean_roots: [src]
`);
  await platform.files.writeText(
    '/project/templates/{model}/[model.name].ts.hbs',
    'export interface {{pascal model.name}} {}\n',
  );
  const templateSource: ResolvedSource = {
    id: 'templates:baseline',
    descriptor: { kind: 'memory', id: 'templates:baseline' },
    root: '/project/templates',
    entry: '/project/templates/paths.yaml',
    digest: 'templates-baseline',
    files: [],
  };
  platform.memorySources.register(templateSource);
  const templating = createTemplatingEngine(platform);
  const compiled = await templating.compile({
    source: { kind: 'memory', id: 'templates:baseline' },
  });
  assert.equal(compiled.success, true);
  if (!compiled.success) return;
  const compiledAgain = await templating.compile({
    source: { kind: 'memory', id: 'templates:baseline' },
    cache: 'bypass',
  });
  assert.equal(compiledAgain.success, true);
  if (!compiledAgain.success) return;
  assert.deepEqual(compiledAgain.value, compiled.value);
  assertJsonSafe(compiled.value);

  const template = compiled.value.templates[0];
  assert.ok(template);
  const model = authoring.schemas[0];
  assert.ok(model);
  const outputPath = resolveOutputTokens(template.outputTokens, { model });
  const renderedTemplate = await templating.render({
    templates: compiled.value,
    files: [{ templateId: template.id, outputPath, context: { model } }],
  });
  assert.equal(renderedTemplate.success, true);
  if (!renderedTemplate.success) return;
  const renderedTemplateText = renderedTemplate.value[0]?.content.encoding === 'utf8'
    ? renderedTemplate.value[0].content.text
    : '';
  assert.deepEqual({
    artifactKind: compiled.value.header.kind,
    packName: compiled.value.manifest.name,
    templateCount: compiled.value.templates.length,
    outputPath,
    renderedText: renderedTemplateText,
  }, baseline.templating);

  await platform.files.writeText('/project/CodepotFile.yml', `
allow: true
tasks:
  models:
    authoring: contracts
    templates: templates
    output: generated
    clean: [src]
sources:
  contracts:
    type: memory
    id: contracts
  templates:
    type: memory
    id: templates:baseline
`);
  const authoringPort = {
    compile: async () => ({ success: true, value: authoring, diagnostics: [] }),
  } as unknown as AuthoringPort;
  const generation = createGenerationEngine({
    ...platform,
    authoring: authoringPort,
    templating,
  });
  const loaded = await generation.load({ projectRoot: '/project' });
  assert.equal(loaded.success, true);
  if (!loaded.success) return;
  const plan = await generation.plan({
    codepotFile: loaded.value,
    task: 'models',
    authoring,
    templates: compiled.value,
  });
  assert.equal(plan.success, true);
  if (!plan.success) return;
  const planAgain = await generation.plan({
    codepotFile: loaded.value,
    task: 'models',
    authoring,
    templates: compiled.value,
  });
  assert.equal(planAgain.success, true);
  if (!planAgain.success) return;
  assert.deepEqual(planAgain.value, plan.value);
  assertJsonSafe(plan.value);

  const rendered = await generation.render({
    plan: plan.value,
    templates: compiled.value,
    cache: 'bypass',
  });
  assert.equal(rendered.success, true);
  if (!rendered.success) return;
  assertJsonSafe(rendered.value);
  const renderedText = rendered.value.files[0]?.content.encoding === 'utf8'
    ? rendered.value.files[0].content.text
    : '';
  assert.deepEqual({
    task: plan.value.task,
    outputRoot: plan.value.outputRoot,
    plannedFiles: plan.value.files.map((file) => file.outputPath),
    clean: plan.value.clean.map((item) => ({
      path: item.path,
      allowed: item.allowed,
    })),
    renderedFiles: rendered.value.files.map((file) => file.path),
    renderedText,
  }, baseline.generation);
});
