import type { ResourceContext } from '../core/authoring.types';
import { normalizeInfo, ownerFromResource } from '../core/normalize';
import type { RuntimeHookDefinition, RuntimeHookRegistry } from './hooks.types';
export function defineHooks<const TInput extends Record<string, RuntimeHookDefinition>>(
  input: TInput,
  options: { readonly resource?: ResourceContext } = {},
): RuntimeHookRegistry<TInput> {
  const owner = ownerFromResource(options.resource);
  const definitions = Object.entries(input).map(([key, value]) => {
    const info = value.info ? normalizeInfo(value.info) : undefined;
    const { info: _ignored, ...rest } = value;
    return { ...rest, key, owner, ...(info ? { info } : {}) };
  });
  const ref = Object.fromEntries(definitions.map((definition) => [definition.key, { key: definition.key, name: definition.key, definition }])) as RuntimeHookRegistry<TInput>['ref'];
  return { owner, definitions, ref };
}
