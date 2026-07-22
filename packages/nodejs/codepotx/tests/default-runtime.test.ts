import assert from 'node:assert/strict';
import test from 'node:test';

import { createMemoryPlatformServices } from '../src/platform/index';
import { composeDefaultCodepotRuntime } from '../src/runtime/index';

test('default runtime composes all layers through injected services', async () => {
  const platform = createMemoryPlatformServices();
  const { runtime } = composeDefaultCodepotRuntime({ platform });
  const result = await runtime.features();
  assert.deepEqual(result.features.map((feature) => feature.id), ['authoring', 'templating', 'generation']);
  assert.equal(runtime.events, platform.events);
});
