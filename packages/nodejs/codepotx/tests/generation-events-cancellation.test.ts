import assert from 'node:assert/strict';
import test from 'node:test';

import type {
  CodepotEvent,
  FileWriterPort,
  GenerationPlan,
  RenderedGeneration,
} from '../src/contract/index';
import {
  applyManagedWrite,
  GenerationEventPublisher,
  ManagedWriteError,
} from '../src/generation/index';
import {
  CodepotCancellationController,
  createMemoryPlatformServices,
} from '../src/platform/index';

test('generation publisher emits observational stage file and command events', async () => {
  const platform = createMemoryPlatformServices();
  const events: CodepotEvent[] = [];
  const subscription = platform.events.subscribe((event) => {
    events.push(event);
  });
  const publisher = new GenerationEventPublisher(platform, 'sdk', 'generation:test');
  await publisher.stage('stage.started', 'render');
  await publisher.file({ path: 'src/user.ts', status: 'created', lifecycle: 'managed' });
  await publisher.command({
    id: 'command:format', phase: 'after', command: 'format', cwd: '/project',
    exitCode: 0, skipped: false, optional: false, stdout: '', stderr: '',
  });
  await publisher.stage('stage.completed', 'render', { itemCount: 1 });
  subscription.dispose();

  assert.deepEqual(events.map((event) => event.type), [
    'runtime.stage',
    'generation.file.written',
    'generation.command.completed',
    'runtime.stage',
  ]);
  assert.deepEqual(events.map((event) => event.sequence), [1, 2, 3, 4]);
  assert.equal(events.every((event) => event.runId === 'generation:test'), true);
});

test('cancellation after file mutation rolls back bytes and manifest', async () => {
  const platform = createMemoryPlatformServices();
  await platform.files.mkdir('/project/generated', { recursive: true });
  await platform.files.writeText('/project/generated/file.ts', 'previous\n');
  const controller = new CodepotCancellationController();
  const writer: FileWriterPort = {
    compare: (request) => platform.writer.compare(request),
    write: (request) => platform.writer.write(request),
    writeBatch: async (request) => {
      const outcomes = await platform.writer.writeBatch(request);
      controller.abort('cancel-after-write');
      return outcomes;
    },
  };
  const plan = {
    header: {
      kind: 'codepot.generation-plan', protocolVersion: 1, artifactVersion: 1,
      producer: { name: 'test', version: '1' }, contentDigest: 'plan', sourceDigest: 'source',
    },
    task: 'sdk', projectRoot: '/project', outputRoot: '/project/generated',
    authoring: { kind: 'codepot.authoring', contentDigest: 'a', sourceDigest: 'a' },
    templates: { kind: 'codepot.templates', contentDigest: 't', sourceDigest: 't' },
    files: [], commands: [], clean: [], diagnostics: [],
  } as GenerationPlan;
  const rendered = {
    header: {
      kind: 'codepot.rendered-generation', protocolVersion: 1, artifactVersion: 1,
      producer: { name: 'test', version: '1' }, contentDigest: 'rendered', sourceDigest: 'plan',
    },
    plan: { kind: 'codepot.generation-plan', contentDigest: 'plan', sourceDigest: 'source' },
    files: [{
      id: 'virtual:file', path: 'file.ts', lifecycle: 'managed', compareMode: 'exact',
      content: { encoding: 'utf8', text: 'changed\n' }, contentDigest: 'changed',
      metadata: { templateId: 'template:file' },
    }],
    diagnostics: [],
  } as RenderedGeneration;

  await assert.rejects(
    applyManagedWrite({
      task: 'sdk', projectRoot: '/project', outputRoot: '/project/generated',
      plan, rendered, dryRun: false, transactional: true, signal: controller.signal,
    }, { ...platform, writer }),
    (caught: unknown) => caught instanceof ManagedWriteError && caught.rollback.length > 0,
  );
  assert.equal(await platform.files.readText('/project/generated/file.ts'), 'previous\n');
  assert.equal(await platform.files.exists('/project/.codepot/manifests/sdk.json'), false);
});
