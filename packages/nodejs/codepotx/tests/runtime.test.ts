import assert from 'node:assert/strict';
import test from 'node:test';

import type {
  AuthoringPort,
  GenerationPort,
  OperationResult,
  TemplateIntrospectionPort,
  TemplatingPort,
} from '@/contract/index';
import { CodepotCancellationController } from '../src/platform/cancellation';
import { SequentialEventBus } from '../src/platform/event-bus';
import { FixedClock, SequentialIdProvider } from '../src/platform/system';
import { CodepotRuntime } from '../src/runtime/runtime';

function success(value: unknown = {}): OperationResult<unknown> {
  return { success: true, value, diagnostics: [] };
}

const authoring = {
  compile: async () => success({ compiled: true }),
  validate: async () => success({ valid: true }),
  inspect: async () => success({}),
  loadArtifact: async () => success({}),
  cache: async () => success(null),
} as unknown as AuthoringPort;

const templating = {
  load: async () => success({}),
  validate: async () => success({ valid: true }),
  compile: async () => success({}),
  createContext: async () => success({}),
  render: async () => success([]),
  variables: async () => success({}),
  validateContext: async () => success({ valid: true, diagnostics: [] }),
} as unknown as TemplatingPort & TemplateIntrospectionPort;

const generation = {
  load: async () => success({}),
  plan: async () => success({}),
  render: async () => success({}),
  write: async () => success([]),
  clean: async () => success([]),
  runCommands: async () => success([]),
  execute: async () => success([]),
} as unknown as GenerationPort;

test('runtime dispatches typed operations and keeps observer errors isolated', async () => {
  const events = new SequentialEventBus();
  const received: string[] = [];
  events.subscribe((event) => { received.push(event.type); });
  events.subscribe(() => {
    throw new Error('observer failure');
  });
  const runtime = new CodepotRuntime({
    authoring,
    templating,
    generation,
    events,
    clock: new FixedClock('2026-01-01T00:00:00.000Z'),
    ids: new SequentialIdProvider(),
    features: [{ id: 'authoring.compile', version: '1', layer: 'authoring', capabilities: ['compile'] }],
  });

  const response = await runtime.execute({ kind: 'authoring.compile', input: { source: { kind: 'memory', id: 'contracts' } } });
  assert.equal(response.result.success, true);
  assert.deepEqual(received, ['runtime.started', 'runtime.completed']);
  assert.equal((await runtime.features({ capability: 'compile' })).features.length, 1);
});

test('runtime converts cancellation into a structured failure', async () => {
  const controller = new CodepotCancellationController();
  controller.abort('cancelled before dispatch');
  const runtime = new CodepotRuntime({
    authoring,
    templating,
    generation,
    events: new SequentialEventBus(),
    clock: new FixedClock('2026-01-01T00:00:00.000Z'),
    ids: new SequentialIdProvider(),
  });

  const response = await runtime.execute({
    kind: 'authoring.compile',
    input: { source: { kind: 'memory', id: 'contracts' } },
    context: { signal: controller.signal },
  });
  assert.equal(response.result.success, false);
  assert.equal(response.result.diagnostics[0]?.code, 'RUNTIME_CANCELLED');
});
