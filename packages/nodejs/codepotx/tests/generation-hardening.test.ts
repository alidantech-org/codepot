import assert from 'node:assert/strict';
import test from 'node:test';

import type {
  AuthoringPort,
  CompiledAuthoringArtifact,
  CompiledTemplatePack,
  ResolvedSource,
} from '../src/contract/index';
import {
  createGenerationEngine,
  planFiles,
} from '../src/generation/index';
import {
  createMemoryPlatformServices,
  MemoryCommandRunner,
} from '../src/platform/index';
import {
  buildTemplateContext,
  createTemplatingEngine,
} from '../src/templating/index';

function artifact(schemaNames: readonly string[]): CompiledAuthoringArtifact {
  return {
    header: {
      kind: 'codepot.authoring', protocolVersion: 1, artifactVersion: 1,
      producer: { name: 'test', version: '1' },
      contentDigest: `authoring:${schemaNames.join(',')}`, sourceDigest: 'source',
    },
    source: {
      id: 'authoring', descriptor: { kind: 'memory', id: 'authoring' }, root: '/authoring',
      entry: '/authoring/codepotx.config.ts', digest: 'source', files: [],
    },
    project: { name: 'Generation Demo', version: '1.0.0', tags: [], defaults: {} },
    properties: [],
    schemas: schemaNames.map((name, index) => ({
      id: `schema:${name.toLowerCase()}`,
      key: name,
      name,
      group: 'models',
      role: 'model',
      schema: {
        kind: 'object' as const,
        fields: index === 0 && schemaNames[1]
          ? [{
              id: `field:${name}:dependency`, key: 'dependency', name: 'dependency', wireName: 'dependency',
              schema: { kind: 'ref' as const, ref: `schema:${schemaNames[1].toLowerCase()}`, required: true, nullable: false },
              lifecycle: { selectable: true, editable: true, immutable: false, managed: false },
              query: { enabled: false, filterable: false, searchable: false, sortable: false, operators: [] },
            }]
          : [],
        extends: [],
        additionalProperties: false,
      },
    })),
    entities: [], relations: [], resources: [], operations: [], access: [], hooks: [], frontends: [],
    metadata: {}, diagnostics: [],
  };
}

async function setupProject(afterCommand?: string): Promise<{
  readonly platform: ReturnType<typeof createMemoryPlatformServices>;
  readonly templates: CompiledTemplatePack;
}> {
  const platform = createMemoryPlatformServices();
  await platform.files.mkdir('/project/templates/{model}', { recursive: true });
  await platform.files.writeText('/project/CodepotFile.yml', `
allow: true
tasks:
  models:
    authoring: authoring
    templates: templates
    output: generated
    clean: [src]
    transactional: true
${afterCommand ? `    after:\n      - run: ${afterCommand}` : ''}
sources:
  authoring:
    type: memory
    id: authoring
  templates:
    type: memory
    id: templates
`);
  await platform.files.writeText('/project/templates/paths.yaml', `
name: models
folders:
  model:
    select: schemas.models
    as: model
    mode: each
    parts: [src]
write:
  clean_roots: [src]
`);
  await platform.files.writeText(
    '/project/templates/{model}/[model.name.snake].ts.hbs',
    '{{#each model.emit.imports}}// {{importPath}}\n{{/each}}export interface {{model.name.pascal}} {}\n',
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
  assert.equal((user?.context.model as { emit?: { imports?: readonly { importPath: string }[] } })?.emit?.imports?.[0]?.importPath, './role');
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

test('manifest cleanup deletes only unchanged stale managed files and reports no-change runs', async () => {
  const { platform } = await setupProject();
  let current = artifact(['User', 'Role']);
  const authoring = { compile: async () => ({ success: true as const, value: current, diagnostics: [] }) } as unknown as AuthoringPort;
  const templating = createTemplatingEngine(platform);
  const generation = createGenerationEngine({ ...platform, authoring, templating });

  const first = await generation.execute({ codepotFile: { projectRoot: '/project' }, task: 'models' });
  assert.equal(first.success, true);
  assert.equal(await platform.files.exists('/project/generated/src/role.ts'), true);
  assert.equal(await platform.files.exists('/project/.codepot/manifests/models.json'), true);

  current = artifact(['User']);
  const second = await generation.execute({ codepotFile: { projectRoot: '/project' }, task: 'models' });
  assert.equal(second.success, true);
  if (!second.success) return;
  assert.equal(await platform.files.exists('/project/generated/src/role.ts'), false);
  assert.equal(second.value[0]?.files.some((file) => file.status === 'deleted'), true);

  const third = await generation.execute({ codepotFile: { projectRoot: '/project' }, task: 'models' });
  assert.equal(third.success, true);
  if (!third.success) return;
  assert.equal(third.value[0]?.files.some((file) => file.status === 'unchanged'), true);
  assert.equal(third.value[0]?.report.fileCounts.unchanged, 1);
});

test('modified stale managed files are preserved', async () => {
  const { platform } = await setupProject();
  let current = artifact(['User', 'Role']);
  const authoring = { compile: async () => ({ success: true as const, value: current, diagnostics: [] }) } as unknown as AuthoringPort;
  const generation = createGenerationEngine({ ...platform, authoring, templating: createTemplatingEngine(platform) });
  assert.equal((await generation.execute({ codepotFile: { projectRoot: '/project' }, task: 'models' })).success, true);
  await platform.files.writeText('/project/generated/src/role.ts', '// user edited\n');
  current = artifact(['User']);
  const result = await generation.execute({ codepotFile: { projectRoot: '/project' }, task: 'models' });
  assert.equal(result.success, true);
  if (!result.success) return;
  assert.equal(await platform.files.readText('/project/generated/src/role.ts'), '// user edited\n');
  assert.equal(result.value[0]?.files.some((file) => file.status === 'refused'), true);
});

test('required after-command failure rolls back files and manifest', async () => {
  const { platform } = await setupProject('fail');
  const commands = new MemoryCommandRunner((request) => ({
    command: request.command,
    cwd: request.cwd,
    exitCode: request.command === 'fail' ? 1 : 0,
    stdout: '',
    stderr: request.command === 'fail' ? 'failed' : '',
    skipped: false,
  }));
  const authoring = { compile: async () => ({ success: true as const, value: artifact(['User']), diagnostics: [] }) } as unknown as AuthoringPort;
  const generation = createGenerationEngine({
    ...platform,
    commands,
    authoring,
    templating: createTemplatingEngine(platform),
  });
  const result = await generation.execute({ codepotFile: { projectRoot: '/project' }, task: 'models' });
  assert.equal(result.success, false);
  assert.equal(await platform.files.exists('/project/generated/src/user.ts'), false);
  assert.equal(await platform.files.exists('/project/.codepot/manifests/models.json'), false);
  assert.equal(result.diagnostics.some((item) => item.code === 'GENERATION_ROLLBACK_COMPLETED'), true);
});
