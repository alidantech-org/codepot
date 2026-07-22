import assert from 'node:assert/strict';
import test from 'node:test';

import type { CompiledAuthoringArtifact, ResolvedSource } from '../src/contract/index';
import { createMemoryPlatformServices } from '../src/platform/index';
import { createTemplatingEngine, resolveOutputTokens } from '../src/templating/index';

test('paths.yaml compiles and Handlebars renders virtual files in memory', async () => {
  const platform = createMemoryPlatformServices();
  await platform.files.mkdir('/templates/{model}', { recursive: true });
  await platform.files.writeText('/templates/paths.yaml', `
name: test-pack
template_extension: .hbs
helpers: [pascal]
folders:
  model:
    select: authoring.schemas
    as: model
    mode: each
    parts:
      - src
      - models
      - [model.name]
`);
  await platform.files.writeText('/templates/{model}/[model.name].ts.hbs', 'export interface {{pascal model.name}} {}\n');
  const source: ResolvedSource = {
    id: 'templates:test',
    descriptor: { kind: 'memory', id: 'templates:test' },
    root: '/templates',
    entry: '/templates/paths.yaml',
    digest: 'templates-digest',
    files: [],
  };
  platform.memorySources.register(source);
  const engine = createTemplatingEngine(platform);
  const compiled = await engine.compile({ source: { kind: 'memory', id: 'templates:test' } });
  assert.equal(compiled.success, true);
  if (!compiled.success) return;
  assert.equal(compiled.value.templates.length, 1);
  const template = compiled.value.templates[0]!;
  const outputPath = resolveOutputTokens(template.outputTokens, { model: { name: 'user_profile' } });
  assert.equal(outputPath, 'src/models/user_profile/user_profile.ts');
  const rendered = await engine.render({
    templates: compiled.value,
    files: [{ templateId: template.id, outputPath, context: { model: { name: 'user_profile' } } }],
  });
  assert.equal(rendered.success, true);
  if (!rendered.success) return;
  assert.equal(rendered.value[0]?.content.encoding, 'utf8');
  assert.equal(rendered.value[0]?.content.encoding === 'utf8' ? rendered.value[0].content.text : '', 'export interface UserProfile {}\n');
});

test('templating context is created from stable artifacts only', async () => {
  const platform = createMemoryPlatformServices();
  const engine = createTemplatingEngine(platform);
  const authoring = {
    header: {
      kind: 'codepot.authoring', protocolVersion: 1, artifactVersion: 1,
      producer: { name: 'test', version: '1' }, contentDigest: 'a', sourceDigest: 'a',
    },
    source: {
      id: 'a', descriptor: { kind: 'memory', id: 'a' }, root: '/', entry: '/config.ts', digest: 'a', files: [],
    },
    project: { name: 'Demo', version: '1', tags: [], defaults: {} },
    properties: [], schemas: [], entities: [], relations: [], resources: [], operations: [],
    access: [], hooks: [], frontends: [{ id: 'web', key: 'web', name: 'web', components: [], screens: [] }],
    metadata: {}, diagnostics: [],
  } as CompiledAuthoringArtifact;
  const context = await engine.createContext({ authoring, templates: {} as never, selectedFrontend: 'web', variables: { package: 'demo' } });
  assert.equal(context.success, true);
  if (context.success) assert.deepEqual(context.value.variables, { package: 'demo' });
});
