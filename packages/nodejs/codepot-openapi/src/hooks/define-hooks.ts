import type { RuntimeHookDefinition, RuntimeHookOwner, RuntimeHookRegistry } from './runtime-hooks.types.js';

export interface DefineHooksOptions {
  readonly owner: RuntimeHookOwner;
}

export function defineHooks<const TInput extends Record<string, RuntimeHookDefinition>>(
  input: TInput,
  options: DefineHooksOptions,
): RuntimeHookRegistry<TInput> {
  const definitions = Object.entries(input).map(([key, definition]) => ({
    key,
    owner: options.owner,
    ...definition,
  })) as RuntimeHookRegistry<TInput>['definitions'];

  const ref = Object.fromEntries(
    definitions.map((definition) => [
      definition.key,
      {
        key: definition.key,
        name: definition.key,
        phase: definition.phase,
        owner: options.owner,
        definition,
      },
    ]),
  ) as unknown as RuntimeHookRegistry<TInput>['ref'];

  return {
    owner: options.owner,
    definitions,
    ref,
  };
}
