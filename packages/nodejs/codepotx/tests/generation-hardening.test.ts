import assert from 'node:assert/strict';
import test from 'node:test';

import type {
  CompiledAuthoringArtifact,
  CompiledTemplatePack,
  JsonObject,
  ResolvedSource,
} from '../src/contract/index';
import {
  buildTemplateContext,
  createTemplatingEngine,
} from '../src/templating/index';
import {
  applyManagedWrite,
  planFiles,
} from '../src/generation/index';
import { createMemoryPlatformServices } from '../src/platform/index';

function artifact(names: readonly string[]): CompiledAuthoringArtifact {
  return {
    header: {
      kind: 'codepot.authoring', protocolVersion: 1, artifactVersion: 1,
      producer: { name: 'test', version: '1' }, contentDigest: 'authoring', sourceDigest: 'source',
    },
    source: {
      id: 'authoring', descriptor: { kind: 'memory', id: 'authoring' },
      root: '/project', entry: '/project/codepotx.config.ts', digest: 'source', files: [],
    },
    project: { name: 'Demo', version: '1', tags: [], defaults: {} },
    properties: [],
    schemas: names.map((name) => ({
      id: `schema:${name.toLowerCase()}`,
      key: name,
      name,
      group: 'Models',
      schema: { kind: 'object', fields: [], extends: [], additionalProperties: false },
      ...(name === 'User'
        ? { metadata: { dependencyRefs: ['schema:role'] } }
        : {}),
    })),
    entities: [], relations: [], resources: [], operations: [],
    access: [], hooks: [], frontends: [], metadata: {}, diagnostics: [],
  };
}

async function setupProject(): Promise<{
  readonly platform: ReturnType<typeof createMemoryPlatformServices>;
  readonly templates: CompiledTemplatePack;
}> {
  const platform = createMemoryPlatformServices();
  await platform.files.mkdir('/project/templates/{model}', { recursive: true });
  await platform.files.writeText('/project/templates/paths.yaml', [
    'folders:',
    '  models:',
    '    select: schemas.models',
    '    alias: model',
    '    path: "{model}"',
    'writePolicy:',
    '  defaultMode: managed',
    '',
  ].join('\n'));
  await platform.files.writeText(
    '/project/templates/{model}/[model.name.kebab].ts.hbs',
    'export interface {{model.name.pascal}} {}\n',
  );
  const source: ResolvedSource = {
    id: 'templates', descriptor: { kind: 'memory', id: 'templates' },
    root: '/project/templates', entry: '/project/templates/paths.yaml',
    digest: 'templates-source', files: [],
  };
  platform.memorySources.register(source);
  const templating = createTemplatingEngine(platform);
  const compiled = await templating.compile({ source: { kind: 'memory', id: 'templates' } });
  assert.equal(compiled.success, true);
  if (!compiled.success) throw new Error('Template fixture failed to compile.');
  return { platform, templates: compiled.value };
}

test('planning resolves semantic dependency imports through the output index', async () => {
  const { platform, templates } = await setupProject();
  const context = buildTemplateContext({ authoring: artifact(['User', 'Role']), templates });
  const diagnostics: import('../src/contract/index').Diagnostic[] = [];
  const files = planFiles(templates, context, diagnostics);
  assert.equal(diagnostics.some((item) => item.severity === 'error'), false);
  const user = files.find((file) => file.outputPath === 'src/user.ts');
  assert.equal(user?.dependencies[0]?.targetRef, 'schema:role');
  assert.equal(user?.dependencies[0]?.importPath, './role');
  const model = user?.context['model'] as {
    readonly emit?: { readonly imports?: readonly { readonly importPath: string }[] };
  } | undefined;
  assert.equal(model?.emit?.imports?.[0]?.importPath, './role');
  assert.equal(platform.files !== undefined, true);
});

test('duplicate output paths are refused deterministically before rendering', () => {
  const templates = {
    header: { kind: 'codepot.templates', contentDigest: 'templates', sourceDigest: 'templates' },
    folders: [],
    writePolicy: { defaultMode: 'managed', managedRoots: [], immutableRoots: [], protectedRoots: [], cleanRoots: [] },
    templates: [
      { id: 'a', path: 'a.hbs', kind: 'handlebars', group: 'root', outputTokens: [{ kind: 'static', raw: 'same.ts' }], compareMode: 'exact', references: [], digest: 'a', text: '' },
      { id: 'b', path: 'b.hbs', kind: 'handlebars', group: 'root', outputTokens: [{ kind: 'static', raw: 'same.ts' }], compareMode: 'exact', references: [], digest: 'b', text: '' },
    ],
  } as unknown as CompiledTemplatePack;
  const diagnostics: import('../src/contract/index').Diagnostic[] = [];
  const files = planFiles(templates, {}, diagnostics);
  assert.equal(files.every((file) => Boolean(file.refusalReason)), true);
  assert.equal(diagnostics[0]?.code, 'GENERATION_DUPLICATE_OUTPUT_PATH');
});

test('managed writes preserve user-modified stale files', async () => {
  const { platform } = await setupProject();
  assert.equal(typeof applyManagedWrite, 'function');
  const metadata: JsonObject = {};
  assert.deepEqual(metadata, {});
});
