import { normalizeInfo, ownerFromResource } from '../core/normalize';
import type { ResourceContext } from '../core/authoring.types';
import type { AccessBuilder, AccessDefinitionInput, AccessDefinitionObject, AccessRegistry, AccessRoleSources } from './access.types';
import type { ComponentRef } from '../refs/ref.types';
import type { InfoInput } from '../core/authoring.types';

export function createAccessBuilder(): AccessBuilder {
  return new FluentAccessBuilder();
}

export function defineAccess<const TInput extends Record<string, AccessDefinitionInput>>(
  input: TInput,
  options: { readonly resource?: ResourceContext } = {},
): AccessRegistry<TInput> {
  const owner = ownerFromResource(options.resource);
  const definitions = Object.entries(input).map(([key, raw]) => {
    const value = 'build' in raw ? raw.build() : raw;
    return {
      ...value,
      key,
      owner,
      ...(value.info ? { info: normalizeInfo(value.info as InfoInput) } : {}),
    };
  }) as AccessRegistry<TInput>['definitions'];
  const ref = Object.fromEntries(definitions.map((definition) => [definition.key, {
    key: definition.key,
    name: definition.key,
    owner,
    definition,
  }])) as AccessRegistry<TInput>['ref'];
  return { owner, definitions, ref };
}

class FluentAccessBuilder implements AccessBuilder {
  #value: AccessDefinitionObject = { context: null };
  context(context: ComponentRef | null): AccessBuilder { this.#value = { ...this.#value, context }; return this; }
  roles(roles: AccessRoleSources): AccessBuilder { this.#value = { ...this.#value, roles }; return this; }
  tags(tags: readonly string[]): AccessBuilder { this.#value = { ...this.#value, tags: [...tags] }; return this; }
  description(description: string): AccessBuilder { this.#value = { ...this.#value, description }; return this; }
  info(info: InfoInput): AccessBuilder { this.#value = { ...this.#value, info }; return this; }
  build(): AccessDefinitionObject { return { ...this.#value }; }
}
