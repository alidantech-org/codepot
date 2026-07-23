import type { RunContext } from '@/contract/index';
import { success } from '@/internal/results/operation-results';
import type { RuntimeDependencies } from '../runtime-dependencies.types';
import type { RuntimeOperationHandlerRegistry } from './runtime-handler.types';
import { selectRuntimeFeatures } from './select-runtime-features';

export function createRuntimeOperationHandlers(
  dependencies: RuntimeDependencies,
): RuntimeOperationHandlerRegistry {
  const features = dependencies.features ?? [];
  return {
    'authoring.compile': (input) => dependencies.authoring.compile(input),
    'authoring.validate': (input) => dependencies.authoring.validate(input),
    'authoring.inspect': (input) => dependencies.authoring.inspect(input),
    'authoring.artifact.load': (input) => dependencies.authoring.loadArtifact(input),
    'authoring.cache': (input) => dependencies.authoring.cache(input),
    'templating.load': (input) => dependencies.templating.load(input),
    'templating.validate': (input) => dependencies.templating.validate(input),
    'templating.compile': (input) => dependencies.templating.compile(input),
    'templating.context': (input) => dependencies.templating.createContext(input),
    'templating.variables': (input) => dependencies.templating.variables(input),
    'templating.context.validate': (input) => dependencies.templating.validateContext(input),
    'templating.render': (input) => dependencies.templating.render(input),
    'generation.file.load': (input) => dependencies.generation.load(input),
    'generation.plan': (input, context) =>
      dependencies.generation.plan(inheritRunSignal(input, context)),
    'generation.render': (input, context) =>
      dependencies.generation.render(inheritRunSignal(input, context)),
    'generation.write': (input, context) =>
      dependencies.generation.write(inheritRunSignal(input, context)),
    'generation.clean': (input, context) =>
      dependencies.generation.clean(inheritRunSignal(input, context)),
    'generation.commands': (input, context) =>
      dependencies.generation.runCommands(inheritRunSignal(input, context)),
    'generation.execute': (input, context) =>
      dependencies.generation.execute(inheritRunSignal(input, context)),
    'runtime.features': async (input) =>
      success({ features: selectRuntimeFeatures(features, input) }),
  } satisfies RuntimeOperationHandlerRegistry;
}

function inheritRunSignal<TRequest extends { readonly signal?: RunContext['signal'] }>(
  input: TRequest,
  context: RunContext,
): TRequest {
  const signal = context.signal;
  return signal && input.signal === undefined ? { ...input, signal } : input;
}
