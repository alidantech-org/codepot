import assert from 'node:assert/strict';
import test from 'node:test';

import type { AuthoringPort, CompiledAuthoringArtifact, ResolvedSource } from '../src/contract/index';
import { createGenerationEngine } from '../src/generation/index';
import { createMemoryPlatformServices } from '../src/platform/index';
import { createTemplatingEngine } from '../src/templating/index';

function authoringFixture(): CompiledAuthoringArtifact {
  return {
    header: {
      kind: 'codepot.authoring', protocolVersion: 1, artifactVersion: 1,
      producer: { name: 'test', version: '1' }, contentDigest: 'authoring', sourceDigest: 'source',
    },
    source: {
      id: 'contracts', descriptor: { kind: 'memory', id: 'contracts' }, root: '/contracts',
      entry: '/contracts/codepotx.config.ts', digest: 'source', files: [],
    },
    project: { name: 'Demo', version: '1.0.0', tags: [], defaults: {} },
    properties: [],
    schemas: [{
      id: 'schema:user', key: 'User', name: 'user_profile', group: 'models', role: 'model',
      schema: { kind: 'object', fields: [], extends: [], additionalProperties: false },
    }],
    entities: [], relations: [], resources: [], operations: [], access: [], hooks: [], frontends: [],
    metadata: {}, diagnostics: [],
  };
}

test('CodepotFile planning renders and writes generated files through memory adapters', async () => {
  const platform = createMemoryPlatformServices();
  await platform.files.mkdir('/project/templates/{model}', { recursive: true });
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
    id: templates
`);
  await platform.files.writeText('/project/templates/paths.yaml', `
name: models
helpers: [pascal]
folders:
  model:
    select: authoring.schemas
    as: model
    mode: each
    parts: [src]
write:
  clean_roots: [src]
`);
  await platform.files.writeText('/project/templates/{model}/[model.name].ts.hbs', 'export interface {{pascal model.name}} {}\n');

  const templateSource: ResolvedSource = {
    id: 'templates',
    descriptor: { kind: 'memory', id: 'templates' },
    root: '/project/templates',
    entry: '/project/templates/paths.yaml',
    digest: 'templates-source',
    files: [],
  };
  platform.memorySources.register(templateSource);
  const templating = createTemplatingEngine(platform);
  const templates = await templating.compile({ source: { kind: 'memory', id: 'templates' } });
  assert.equal(templates.success, true);
  if (!templates.success) return;

  const authoring = authoringFixture();
  const authoringPort = { compile: async () => ({ success: true, value: authoring, diagnostics: [] }) } as unknown as AuthoringPort;
  const generation = createGenerationEngine({ ...platform, authoring: authoringPort, templating });

  const loaded = await generation.load({ projectRoot: '/project' });
  assert.equal(loaded.success, true);
  if (!loaded.success) return;
  const plan = await generation.plan({ codepotFile: loaded.value, task: 'models', authoring, templates: templates.value });
  assert.equal(plan.success, true);
  if (!plan.success) return;
  assert.equal(plan.value.files[0]?.outputPath, 'src/user_profile.ts');
  assert.equal(plan.value.clean[0]?.allowed, true);

  const rendered = await generation.render({ plan: plan.value, templates: templates.value });
  assert.equal(rendered.success, true);
  if (!rendered.success) return;
  const written = await generation.write({ rendered: rendered.value, outputRoot: plan.value.outputRoot });
  assert.equal(written.success, true);
  assert.equal(await platform.files.readText('/project/generated/src/user_profile.ts'), 'export interface UserProfile {}\n');
});

test('unsafe clean paths are refused during planning', async () => {
  const platform = createMemoryPlatformServices();
  const templating = createTemplatingEngine(platform);
  const generation = createGenerationEngine({ ...platform, authoring: {} as AuthoringPort, templating });
  const templates = {
    header: { kind: 'codepot.templates', contentDigest: 't', sourceDigest: 't' }, folders: [], templates: [],
    writePolicy: { defaultMode: 'managed', managedRoots: [], immutableRoots: [], protectedRoots: [], cleanRoots: [] },
  } as never;
  const file = {
    path: '/project/CodepotFile.yml', root: '/project', allow: true, defaults: {},
    tasks: [{
      name: 'bad',
      authoring: { kind: 'memory', id: 'a' },
      templates: { kind: 'memory', id: 't' },
      output: 'generated',
      clean: ['../outside'],
      before: [],
      after: [],
      environment: {},
      transactional: true,
    }],
  } as const;
  const plan = await generation.plan({ codepotFile: file, task: 'bad', authoring: authoringFixture(), templates });
  assert.equal(plan.success, true);
  if (plan.success) assert.equal(plan.value.clean[0]?.allowed, false);
});
