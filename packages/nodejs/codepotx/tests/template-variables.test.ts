import assert from 'node:assert/strict';
import test from 'node:test';

import type { CompiledAuthoringArtifact, ResolvedSource } from '../src/contract/index';
import { createMemoryPlatformServices } from '../src/platform/index';
import { createTemplatingEngine } from '../src/templating/index';

function authoringFixture(): CompiledAuthoringArtifact {
  return {
    header: {
      kind: 'codepot.authoring',
      protocolVersion: 1,
      artifactVersion: 1,
      producer: { name: 'test', version: '1' },
      contentDigest: 'authoring-content',
      sourceDigest: 'authoring-source',
    },
    source: {
      id: 'authoring:test',
      descriptor: { kind: 'memory', id: 'authoring:test' },
      root: '/authoring',
      entry: '/authoring/codepotx.config.ts',
      digest: 'authoring-source',
      files: [],
    },
    project: { name: 'Template Demo', version: '1.0.0', tags: [], defaults: {} },
    properties: [],
    schemas: [{
      id: 'schema:user',
      key: 'user',
      name: 'User Profile',
      group: 'models',
      role: 'model',
      schema: {
        kind: 'object',
        fields: [],
        extends: [],
        additionalProperties: false,
      },
    }],
    entities: [],
    relations: [],
    resources: [],
    operations: [],
    access: [],
    hooks: [],
    frontends: [],
    metadata: {},
    diagnostics: [],
  };
}

test('template variable catalog lists stable Python-compatible context paths', async () => {
  const platform = createMemoryPlatformServices();
  await platform.files.mkdir('/templates/{model}', { recursive: true });
  await platform.files.mkdir('/templates/_partials', { recursive: true });
  await platform.files.writeText('/templates/paths.yaml', `
name: catalog-pack
include_hidden: true
variables:
  required:
    - project.name.pascal
    - schemas.models[].name.snake
folders:
  model:
    mode: each
    select: schemas.models
    as: model
    parts: [src, models, [model.name.snake]]
`);
  await platform.files.writeText('/templates/_partials/banner.hbs', '// {{project.name.title}}\n');
  await platform.files.writeText('/templates/{model}/[model.name.snake].ts.hbs', '{{> banner}}export interface {{model.name.pascal}} {}\n');
  const source: ResolvedSource = {
    id: 'templates:catalog',
    descriptor: { kind: 'memory', id: 'templates:catalog' },
    root: '/templates',
    entry: '/templates/paths.yaml',
    digest: 'templates-source',
    files: [],
  };
  platform.memorySources.register(source);
  const engine = createTemplatingEngine(platform);
  const compiled = await engine.compile({ source: { kind: 'memory', id: 'templates:catalog' } });
  assert.equal(compiled.success, true);
  if (!compiled.success) return;
  assert.deepEqual(compiled.value.manifest.partials, ['banner']);
  const result = await engine.variables({
    authoring: authoringFixture(),
    templates: compiled.value,
    format: 'object',
  });
  assert.equal(result.success, true);
  if (!result.success || typeof result.value === 'string') return;
  const paths = new Set(result.value.entries.map((entry) => entry.path));
  assert.equal(paths.has('project.name.pascal'), true);
  assert.equal(paths.has('schemas.models[].name.snake'), true);
  assert.equal(result.value.partials[0]?.name, 'banner');
  assert.equal(result.value.helpers.some((helper) => helper.name === 'pascal'), true);
});

test('unknown Handlebars variables fail before rendering', async () => {
  const platform = createMemoryPlatformServices();
  await platform.files.mkdir('/templates/{model}', { recursive: true });
  await platform.files.writeText('/templates/paths.yaml', `
folders:
  model:
    mode: each
    select: schemas.models
`);
  await platform.files.writeText('/templates/{model}/model.ts.hbs', '{{model.name.pascal}} {{missing.value}}');
  const source: ResolvedSource = {
    id: 'templates:invalid',
    descriptor: { kind: 'memory', id: 'templates:invalid' },
    root: '/templates',
    entry: '/templates/paths.yaml',
    digest: 'templates-invalid',
    files: [],
  };
  platform.memorySources.register(source);
  const engine = createTemplatingEngine(platform);
  const compiled = await engine.compile({ source: { kind: 'memory', id: 'templates:invalid' } });
  assert.equal(compiled.success, true);
  if (!compiled.success) return;
  const validation = await engine.validateContext({
    authoring: authoringFixture(),
    templates: compiled.value,
    strict: true,
  });
  assert.equal(validation.success, false);
  assert.equal(validation.diagnostics.some((item) => item.code === 'TEMPLATING_UNKNOWN_VARIABLE'), true);
});

test('catalog can be rendered as Markdown for docs and CLI', async () => {
  const platform = createMemoryPlatformServices();
  const engine = createTemplatingEngine(platform);
  const templates = {
    header: {
      kind: 'codepot.templates', protocolVersion: 1, artifactVersion: 1,
      producer: { name: 'test', version: '1' }, contentDigest: 'templates', sourceDigest: 'templates',
    },
    source: {
      id: 'templates:test', descriptor: { kind: 'memory', id: 'templates:test' },
      root: '/templates', entry: '/templates/paths.yaml', digest: 'templates', files: [],
    },
    manifest: {
      name: 'test', version: '1', templateExtension: '.hbs', stripTemplateExtension: true,
      allowRawFiles: true, includeHidden: true, ignore: [], helpers: [], partials: [], variableRequirements: [],
    },
    folders: [],
    writePolicy: { defaultMode: 'managed', managedRoots: [], immutableRoots: [], protectedRoots: [], cleanRoots: [] },
    templates: [],
    files: [],
    diagnostics: [],
  } as const;
  const result = await engine.variables({ authoring: authoringFixture(), templates, format: 'markdown' });
  assert.equal(result.success, true);
  if (result.success) assert.match(String(result.value), /# Codepot template variables/);
});
