import type { RuntimeFeature } from '@/contract/index';

export const DEFAULT_RUNTIME_FEATURES: readonly RuntimeFeature[] = [
  {
    id: 'authoring',
    version: '1',
    layer: 'authoring',
    capabilities: ['load', 'validate', 'compile', 'inspect', 'cache'],
  },
  {
    id: 'templating',
    version: '1',
    layer: 'templating',
    capabilities: [
      'load',
      'validate',
      'compile',
      'context',
      'variables',
      'context-validation',
      'partials',
      'render',
    ],
  },
  {
    id: 'generation',
    version: '1',
    layer: 'generation',
    capabilities: ['load', 'plan', 'render', 'write', 'clean', 'commands', 'execute'],
  },
];
