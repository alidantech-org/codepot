import assert from 'node:assert/strict';
import test from 'node:test';

import type {
  CodepotTaskConfig,
  CompiledTemplatePack,
  RenderedGeneration,
} from '../src/contract/index';
import {
  buildGenerationManifest,
  planClean,
  planCommands,
  planFiles,
  renderCacheKey,
} from '../src/generation/index';
import { createMemoryPlatformServices } from '../src/platform/index';

const templates = {
  header: {
    kind: 'codepot.templates', protocolVersion: 1, artifactVersion: 1,
    producer: { name: 'test', version: '1' }, contentDigest: 'templates', sourceDigest: 'templates',
  },
  source: {
    id: 'templates', descriptor: { kind: 'memory', id: 'templates' }, root: '/templates',
    entry: '/templates/paths.yaml', digest: 'templates', files: [],
  },
  manifest: {
    name: 'test', version: '1', templateExtension: '.hbs', stripTemplateExtension: true,
    allowRawFiles: true, includeHidden: true, ignore: [], helpers: [], partials: [], variableRequirements: [],
  },
  folders: [],
  writePolicy: {
    defaultMode: 'managed', managedRoots: [], immutableRoots: [], protectedRoots: [], cleanRoots: ['src'],
  },
  templates: [{
    id: 'template:file', path: 'file.ts.hbs', kind: 'handlebars', group: 'root',
    outputTokens: [{ kind: 'static', raw: 'src/file.ts' }], compareMode: 'exact',
    references: [], text: 'export {};\n', digest: 'template',
  }],
  files: [], diagnostics: [],
} as CompiledTemplatePack;

const task: CodepotTaskConfig = {
  name: 'sdk',
  authoring: { kind: 'memory', id: 'authoring' },
  templates: { kind: 'memory', id: 'templates' },
  output: 'generated',
  clean: ['src'],
  before: [{ run: 'prepare', optional: false, environment: {} }],
  after: [{ run: 'format', optional: true, environment: {} }],
  environment: {},
  transactional: true,
};

test('planned files commands and clean operations are byte-stable', () => {
  const diagnosticsA: import('../src/contract/index').Diagnostic[] = [];
  const diagnosticsB: import('../src/contract/index').Diagnostic[] = [];
  const filesA = planFiles(templates, {}, diagnosticsA);
  const filesB = planFiles(templates, {}, diagnosticsB);
  assert.deepEqual(filesA, filesB);
  assert.deepEqual(planCommands(task, '/project', false, false), planCommands(task, '/project', false, false));
  assert.deepEqual(planClean(task, '/project/generated', templates), planClean(task, '/project/generated', templates));
});

test('generation manifests and render cache keys are deterministic', async () => {
  const platform = createMemoryPlatformServices();
  const rendered: RenderedGeneration = {
    header: {
      kind: 'codepot.rendered-generation', protocolVersion: 1, artifactVersion: 1,
      producer: { name: 'test', version: '1' }, contentDigest: 'rendered', sourceDigest: 'plan',
    },
    plan: { kind: 'codepot.generation-plan', contentDigest: 'plan', sourceDigest: 'source' },
    files: [{
      id: 'file', path: 'src/file.ts', lifecycle: 'managed', compareMode: 'exact',
      content: { encoding: 'utf8', text: 'export {};\n\n' }, contentDigest: 'raw',
      metadata: { templateId: 'template:file' },
    }],
    diagnostics: [],
  };
  const planRef = { kind: 'codepot.generation-plan' as const, contentDigest: 'plan', sourceDigest: 'source' };
  const left = await buildGenerationManifest('sdk', '/project', '/project/generated', planRef, rendered, platform);
  const right = await buildGenerationManifest('sdk', '/project', '/project/generated', planRef, rendered, platform);
  assert.deepEqual(left, right);
  const fakePlan = { header: { contentDigest: 'plan' } } as never;
  assert.equal(renderCacheKey(fakePlan, templates), renderCacheKey(fakePlan, templates));
});
