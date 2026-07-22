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
