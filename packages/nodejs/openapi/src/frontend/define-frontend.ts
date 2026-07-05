import { createSchemaComponentRegistry, defineSchemas } from '../components/schemas/define-schemas.js';
import type { ComponentFieldMap } from '../components/component.types.js';
import { EngineIdPart, createEngineId } from '../ids/engine-id.js';
import { toSchemaName } from '../naming/schema-name.js';
import type {
  DefineFrontendOptions,
  DefineFrontendComponentsInput,
  DefineFrontendScreensInput,
  FrontendBuilder,
  FrontendComponentBuilderMap,
  FrontendComponentBuilder,
  FrontendComponentDefinition,
  FrontendComponentFactoryRoot,
  FrontendComponentRef,
  FrontendComponentRegistry,
  FrontendComponentsDefinitionBuilder,
  FrontendContext,
  FrontendOperationUsesInput,
  FrontendScreenBuilderMap,
  FrontendScreenBuilder,
  FrontendScreenDefinition,
  FrontendScreenFactoryRoot,
  FrontendScreenRef,
  FrontendScreenRegistry,
  FrontendScreensDefinitionBuilder,
} from './frontend.types.js';
import type { InfoInput } from '../info/info.types.js';
import { normalizeInfo } from '../info/normalize-info.js';

type MutableComponentDefinition = {
  -readonly [K in keyof Omit<FrontendComponentDefinition, 'key' | 'name' | 'tags' | 'uses'>]?: FrontendComponentDefinition[K];
} & {
  tags?: readonly string[];
  uses?: FrontendOperationUsesInput;
};

type MutableScreenDefinition = {
  -readonly [K in keyof Omit<FrontendScreenDefinition, 'key' | 'name' | 'tags' | 'uses' | 'components'>]?: FrontendScreenDefinition[K];
} & {
  tags?: readonly string[];
  uses?: FrontendOperationUsesInput;
  components?: Record<string, FrontendComponentRef>;
};

export function defineFrontend(options: DefineFrontendOptions): FrontendBuilder {
  if (!options.name || !options.name.trim()) {
    throw new Error('Frontend name must be a non-empty string.');
  }

  const context: FrontendContext = {
    name: options.name,
    title: options.title,
    routePrefix: options.routePrefix,
    folders: normalizeList(options.folders),
    tags: normalizeList(options.tags),
    description: options.description,
    info: normalizeInfo(options.info),
  };

  const schemaComponents = [createSchemaComponentRegistry(context.name)];
  const componentRegistries: FrontendComponentRegistry[] = [];
  const screenRegistries: FrontendScreenRegistry[] = [];
  const components = { ref: {} as Record<string, FrontendComponentRef> };
  const screens = { ref: {} as Record<string, FrontendScreenRef> };
  const screenRoutes = new Set<string>();

  function defineComponents(): FrontendComponentsDefinitionBuilder {
    return {
      components(input) {
        return createComponentRegistry(input);
      },
    };
  }

  function createComponentRegistry<const TInput extends FrontendComponentBuilderMap>(
    input: DefineFrontendComponentsInput<TInput>,
  ): FrontendComponentRegistry<TInput> {
    const builtInput = input(createComponentFactoryRoot());
    const definitions: FrontendComponentDefinition[] = [];
    const ref = {} as FrontendComponentRegistry<TInput>['ref'];

    for (const [key, builder] of Object.entries(builtInput)) {
      if (components.ref[key]) {
        throw new Error(`Duplicate frontend component "${key}" in frontend "${context.name}".`);
      }

      const built = getComponentDefinition(builder, key);
      const props = built.props;
      const propsRef = props ? definePropsSchema(context, key, props, schemaComponents[0]) : undefined;
      const definition = normalizeComponentDefinition(key, built, propsRef);
      const componentRef = createComponentRef(context.name, key) as FrontendComponentRegistry<TInput>['ref'][keyof TInput & string];

      definitions.push(definition);
      Object.assign(ref, { [key]: componentRef });
      components.ref[key] = componentRef;
    }

    const registry: FrontendComponentRegistry<TInput> = {
      name: context.name,
      definitions,
      ref,
    };

    componentRegistries.push(registry);
    return registry;
  }

  function defineScreens(): FrontendScreensDefinitionBuilder {
    return {
      screens(input) {
        return createScreenRegistry(input);
      },
    };
  }

  function createScreenRegistry<const TInput extends FrontendScreenBuilderMap>(
    input: DefineFrontendScreensInput<TInput>,
  ): FrontendScreenRegistry<TInput> {
    const builtInput = input(createScreenFactoryRoot());
    const definitions: FrontendScreenDefinition[] = [];
    const ref = {} as FrontendScreenRegistry<TInput>['ref'];

    for (const [key, builder] of Object.entries(builtInput)) {
      if (screens.ref[key]) {
        throw new Error(`Duplicate frontend screen "${key}" in frontend "${context.name}".`);
      }

      const screen = getScreenDefinition(builder, key);

      if (screen.route) {
        const routeKey = normalizeFrontendPath(screen.route);
        if (screenRoutes.has(routeKey)) {
          throw new Error(`Duplicate frontend screen route "${screen.route}" in frontend "${context.name}".`);
        }
        screenRoutes.add(routeKey);
      }

      const definition = normalizeScreenDefinition(key, screen);
      const screenRef = createScreenRef(context.name, key) as FrontendScreenRegistry<TInput>['ref'][keyof TInput & string];

      definitions.push(definition);
      Object.assign(ref, { [key]: screenRef });
      screens.ref[key] = screenRef;
    }

    const registry: FrontendScreenRegistry<TInput> = {
      name: context.name,
      definitions,
      ref,
    };

    screenRegistries.push(registry);
    return registry;
  }

  function setInfo(info: InfoInput): FrontendBuilder {
    const next = normalizeInfo(info);
    (context as FrontendContext & { info?: ReturnType<typeof normalizeInfo> }).info = normalizeInfo([
      ...(context.info ? [context.info] : []),
      ...(next ? [next] : []),
    ]);
    return frontendBuilder;
  }

  const frontendBuilder: FrontendBuilder = {
    context,
    schemaComponents,
    componentRegistries,
    screenRegistries,
    components,
    screens,
    defineComponents,
    defineScreens,
    info: setInfo,
  };

  return frontendBuilder;
}

class ComponentBuilder implements FrontendComponentBuilder {
  private readonly definition: MutableComponentDefinition = {};

  title(title: string): FrontendComponentBuilder {
    this.definition.title = title;
    return this;
  }

  description(description: string): FrontendComponentBuilder {
    this.definition.description = description;
    return this;
  }

  props(props: ComponentFieldMap): FrontendComponentBuilder {
    this.definition.props = props;
    return this;
  }

  uses(uses: FrontendOperationUsesInput): FrontendComponentBuilder {
    this.definition.uses = {
      ...(this.definition.uses ?? {}),
      ...uses,
    };
    return this;
  }

  tags(tags: readonly string[]): FrontendComponentBuilder {
    this.definition.tags = [...tags];
    return this;
  }

  info(info: InfoInput): FrontendComponentBuilder {
    this.definition.info = normalizeInfo(info);
    return this;
  }

  build(): MutableComponentDefinition {
    return this.definition;
  }
}

class ScreenBuilder implements FrontendScreenBuilder {
  private readonly definition: MutableScreenDefinition = {};

  constructor(initial: MutableScreenDefinition = {}) {
    this.definition = { ...initial };
  }

  title(title: string): FrontendScreenBuilder {
    this.definition.title = title;
    return this;
  }

  description(description: string): FrontendScreenBuilder {
    this.definition.description = description;
    return this;
  }

  params(params: unknown): FrontendScreenBuilder {
    this.definition.params = params;
    return this;
  }

  query(query: unknown): FrontendScreenBuilder {
    this.definition.query = query;
    return this;
  }

  uses(uses: FrontendOperationUsesInput): FrontendScreenBuilder {
    this.definition.uses = {
      ...(this.definition.uses ?? {}),
      ...uses,
    };
    return this;
  }

  components(components: Record<string, FrontendComponentRef>): FrontendScreenBuilder {
    this.definition.components = {
      ...(this.definition.components ?? {}),
      ...components,
    };
    return this;
  }

  tags(tags: readonly string[]): FrontendScreenBuilder {
    this.definition.tags = [...tags];
    return this;
  }

  info(info: InfoInput): FrontendScreenBuilder {
    this.definition.info = normalizeInfo(info);
    return this;
  }

  build(): MutableScreenDefinition {
    return this.definition;
  }
}

function createComponentFactoryRoot(): FrontendComponentFactoryRoot {
  return {
    component: () => new ComponentBuilder(),
    widget: () => new ComponentBuilder(),
  };
}

function createScreenFactoryRoot(): FrontendScreenFactoryRoot {
  return {
    screen: (route) => new ScreenBuilder({ route }),
    page: (route) => new ScreenBuilder({ route }),
  };
}

function getComponentDefinition(builder: FrontendComponentBuilder, key: string): MutableComponentDefinition {
  const definition = (builder as FrontendComponentBuilder & { build?: () => MutableComponentDefinition }).build?.();

  if (!definition) {
    throw new Error(`Frontend component "${key}" must be created with c.component() or c.widget().`);
  }

  return definition;
}

function getScreenDefinition(builder: FrontendScreenBuilder, key: string): MutableScreenDefinition {
  const definition = (builder as FrontendScreenBuilder & { build?: () => MutableScreenDefinition }).build?.();

  if (!definition) {
    throw new Error(`Frontend screen "${key}" must be created with s.screen(...) or s.page(...).`);
  }

  return definition;
}

function definePropsSchema(
  context: FrontendContext,
  componentKey: string,
  props: ComponentFieldMap,
  target: ReturnType<typeof createSchemaComponentRegistry>,
): import('../refs/ref-usage.types.js').RefWithUsageMethods<import('../refs/ref.types.js').ComponentRef> {
  const schemaName = toSchemaName(context.name, componentKey, 'Props');
  const registry = defineSchemas(
    {
      name: context.name,
    },
    {
      [schemaName]: props,
    },
    target,
  );

  return registry.ref[schemaName];
}

function normalizeComponentDefinition(
  key: string,
  input: MutableComponentDefinition,
  propsRef: FrontendComponentDefinition['propsRef'],
): FrontendComponentDefinition {
  return {
    key,
    name: key,
    title: input.title,
    description: input.description,
    props: input.props,
    propsRef,
    uses: input.uses ?? {},
    tags: input.tags ?? [],
    info: input.info,
  };
}

function normalizeScreenDefinition(key: string, input: MutableScreenDefinition): FrontendScreenDefinition {
  return {
    key,
    name: key,
    title: input.title,
    description: input.description,
    route: input.route,
    params: input.params,
    query: input.query,
    uses: input.uses ?? {},
    components: input.components ?? {},
    tags: input.tags ?? [],
    info: input.info,
  };
}

function createComponentRef(frontendName: string, key: string): FrontendComponentRef {
  return {
    kind: 'frontend-component',
    id: createEngineId(EngineIdPart.version, 'frontend', frontendName, 'component', key),
    name: key,
    key,
    frontend: frontendName,
  };
}

function createScreenRef(frontendName: string, key: string): FrontendScreenRef {
  return {
    kind: 'frontend-screen',
    id: createEngineId(EngineIdPart.version, 'frontend', frontendName, 'screen', key),
    name: key,
    key,
    frontend: frontendName,
  };
}

function normalizeList(values: readonly string[] | undefined): readonly string[] {
  return values?.map((value) => value.trim()).filter(Boolean) ?? [];
}

function normalizeFrontendPath(path: string): string {
  const normalized = path.replace(/\\/g, '/').replace(/\/+/g, '/').replace(/^\/?/, '/');
  return normalized === '/' ? '/' : normalized.replace(/\/$/, '');
}
