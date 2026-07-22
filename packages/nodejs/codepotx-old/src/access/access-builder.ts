import type { ComponentRef, PropertyRef } from '../refs/ref.types.js';
import type { RefWithUsageMethods } from '../refs/ref-usage.types.js';
import type { AccessDefinitionBuilder, AccessDefinitionObject, AccessRoleSource } from './access.types.js';

export interface AccessBuilder extends AccessDefinitionBuilder {
  public(): AccessBuilder;
  context(context: RefWithUsageMethods<ComponentRef> | ComponentRef | null): AccessBuilder;
  role(realm: string, source: RefWithUsageMethods<PropertyRef> | PropertyRef, allow: Record<string, true>): AccessBuilder;
  tags(tags: readonly string[]): AccessBuilder;
  description(description: string): AccessBuilder;
}

export function createAccessBuilder(): AccessBuilder {
  return {
    public: () => new FluentAccessBuilder().public(),
    context: (context) => new FluentAccessBuilder().context(context),
    role: (realm, source, allow) => new FluentAccessBuilder().role(realm, source, allow),
    tags: (tags) => new FluentAccessBuilder().tags(tags),
    description: (description) => new FluentAccessBuilder().description(description),
    build: () => new FluentAccessBuilder().build(),
  };
}

class FluentAccessBuilder implements AccessBuilder {
  private definition: AccessDefinitionObject = {
    context: null,
  };

  public(): AccessBuilder {
    this.definition = {
      ...this.definition,
      context: null,
    };
    return this;
  }

  context(context: RefWithUsageMethods<ComponentRef> | ComponentRef | null): AccessBuilder {
    this.definition = {
      ...this.definition,
      context,
    };
    return this;
  }

  role(realm: string, source: RefWithUsageMethods<PropertyRef> | PropertyRef, allow: Record<string, true>): AccessBuilder {
    validateAllowMap(allow);

    this.definition = {
      ...this.definition,
      roles: {
        ...(this.definition.roles ?? {}),
        [realm]: {
          source,
          allow,
        } satisfies AccessRoleSource,
      },
    };
    return this;
  }

  tags(tags: readonly string[]): AccessBuilder {
    this.definition = {
      ...this.definition,
      tags,
    };
    return this;
  }

  description(description: string): AccessBuilder {
    this.definition = {
      ...this.definition,
      description,
    };
    return this;
  }

  build(): AccessDefinitionObject {
    return this.definition;
  }
}

function validateAllowMap(allow: Record<string, true>): void {
  for (const [key, enabled] of Object.entries(allow)) {
    if (enabled !== true) {
      throw new Error(`Access allow value for "${key}" must be true. Use only { roleName: true }.`);
    }
  }
}
