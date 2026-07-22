import assert from 'node:assert/strict';
import test from 'node:test';

import type { CodepotRuntimePort } from 'codepotx/contract';

import { parseCliArguments } from '../src/args';
import { executeCliCommand } from '../src/commands';

test('CLI arguments remain frontend-only', () => {
  const options = parseCliArguments(['generate', 'api', '--root', '/project', '--dry-run', '--json']);
  assert.equal(options.command, 'generate');
  assert.equal(options.task, 'api');
  assert.equal(options.projectRoot, '/project');
  assert.equal(options.dryRun, true);
  assert.equal(options.json, true);
});

test('generate maps directly to one typed runtime request', async () => {
  let received: unknown;
  const runtime = {
    events: { publish: async () => {}, subscribe: () => ({ dispose: () => {} }) },
    execute: async (request: unknown) => {
      received = request;
      return { kind: 'generation.execute', runId: 'run', result: { success: true, value: [], diagnostics: [] } };
    },
    features: async () => ({ features: [] }),
  } as unknown as CodepotRuntimePort;
  await executeCliCommand(runtime, parseCliArguments(['generate', 'api', '--root', '/project']));
  assert.deepEqual(received, {
    kind: 'generation.execute',
    input: {
      codepotFile: { projectRoot: '/project' },
      task: 'api',
      allTasks: false,
      dryRun: false,
      refresh: false,
      skipBefore: false,
      skipAfter: false,
      verbose: false,
    },
  });
});

test('variables command composes only typed runtime requests', async () => {
  const received: unknown[] = [];
  const task = {
    name: 'sdk',
    authoring: { kind: 'memory', id: 'authoring' },
    templates: { kind: 'memory', id: 'templates' },
    output: 'generated',
    clean: [], before: [], after: [], environment: {},
    variables: { packageName: 'demo' },
  } as const;
  const runtime = {
    events: { publish: async () => {}, subscribe: () => ({ dispose: () => {} }) },
    execute: async (request: { readonly kind: string }) => {
      received.push(request);
      if (request.kind === 'generation.file.load') {
        return { kind: request.kind, runId: 'run', result: { success: true, value: { root: '/project', tasks: [task] }, diagnostics: [] } };
      }
      if (request.kind === 'authoring.compile') {
        return { kind: request.kind, runId: 'run', result: { success: true, value: { header: {} }, diagnostics: [] } };
      }
      if (request.kind === 'templating.compile') {
        return { kind: request.kind, runId: 'run', result: { success: true, value: { header: {} }, diagnostics: [] } };
      }
      return { kind: request.kind, runId: 'run', result: { success: true, value: '# variables', diagnostics: [] } };
    },
    features: async () => ({ features: [] }),
  } as unknown as CodepotRuntimePort;

  await executeCliCommand(runtime, parseCliArguments(['variables', 'sdk', '--root', '/project']));
  assert.deepEqual(received.map((item) => (item as { kind: string }).kind), [
    'generation.file.load',
    'authoring.compile',
    'templating.compile',
    'templating.variables',
  ]);
  assert.equal((received[3] as { input: { format: string } }).input.format, 'markdown');
});
