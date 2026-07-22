import type { ComponentFieldMap } from '../components/component.types.js';
import type { SchemaComponentRegistry } from '../components/schemas/schema-component.types.js';
import type { ComponentRef, RouteRef } from '../refs/ref.types.js';
import type { InfoInput, NormalizedInfo } from '../info/info.types.js';

export interface DefineFrontendOptions {
  readonly name: string;
  readonly title?: string;
  readonly routePrefix?: string;
  readonly folders?: readonly string[];
  readonly tags?: readonly string[];
  readonly description?: string;
  readonly info?: InfoInput;
}

export interface FrontendContext {
  readonly name: string;
  readonly title?: string;
  readonly routePrefix?: string;
  readonly folders: readonly string[];
  readonly tags: readonly string[];
  readonly description?: string;
  readonly info?: NormalizedInfo;
}

export type FrontendOperationUsesInput = Record<string, RouteRef>;

export interface FrontendComponentRef {
  readonly kind: 'frontend-component';
  readonly id: string;
  readonly name: string;
  readonly key: string;
  readonly frontend: string;
}

export interface FrontendScreenRef {
  readonly kind: 'frontend-screen';
  readonly id: string;
  readonly name: string;
  readonly key: string;
  readonly frontend: string;
}

export interface FrontendComponentDefinition {
  readonly key: string;
  readonly name: string;
  readonly title?: string;
  readonly description?: string;
  readonly props?: ComponentFieldMap;
  readonly propsRef?: ComponentRef;
  readonly uses: FrontendOperationUsesInput;
  readonly tags: readonly string[];
  readonly info?: NormalizedInfo;
}

export interface FrontendScreenDefinition {
  readonly key: string;
  readonly name: string;
  readonly title?: string;
  readonly description?: string;
  readonly route?: string;
  readonly params?: unknown;
  readonly query?: unknown;
  readonly uses: FrontendOperationUsesInput;
  readonly components: Record<string, FrontendComponentRef>;
  readonly tags: readonly string[];
  readonly info?: NormalizedInfo;
}

export interface FrontendComponentBuilder {
  title(title: string): FrontendComponentBuilder;
  description(description: string): FrontendComponentBuilder;
  props(props: ComponentFieldMap): FrontendComponentBuilder;
  uses(uses: FrontendOperationUsesInput): FrontendComponentBuilder;
  tags(tags: readonly string[]): FrontendComponentBuilder;
  info(info: InfoInput): FrontendComponentBuilder;
}

export interface FrontendScreenBuilder {
  title(title: string): FrontendScreenBuilder;
  description(description: string): FrontendScreenBuilder;
  params(params: unknown): FrontendScreenBuilder;
  query(query: unknown): FrontendScreenBuilder;
  uses(uses: FrontendOperationUsesInput): FrontendScreenBuilder;
  components(components: Record<string, FrontendComponentRef>): FrontendScreenBuilder;
  tags(tags: readonly string[]): FrontendScreenBuilder;
  info(info: InfoInput): FrontendScreenBuilder;
}

export interface FrontendComponentFactoryRoot {
  component(): FrontendComponentBuilder;
  widget(): FrontendComponentBuilder;
}

export interface FrontendScreenFactoryRoot {
  screen(route: string): FrontendScreenBuilder;
  page(route: string): FrontendScreenBuilder;
}

export type FrontendComponentBuilderMap = Record<string, FrontendComponentBuilder>;
export type FrontendScreenBuilderMap = Record<string, FrontendScreenBuilder>;
export type DefineFrontendComponentsInput<TInput extends FrontendComponentBuilderMap> = (components: FrontendComponentFactoryRoot) => TInput;
export type DefineFrontendScreensInput<TInput extends FrontendScreenBuilderMap> = (screens: FrontendScreenFactoryRoot) => TInput;

export interface FrontendComponentsDefinitionBuilder {
  components<const TInput extends FrontendComponentBuilderMap>(
    input: DefineFrontendComponentsInput<TInput>,
  ): FrontendComponentRegistry<TInput>;
}

export interface FrontendScreensDefinitionBuilder {
  screens<const TInput extends FrontendScreenBuilderMap>(
    input: DefineFrontendScreensInput<TInput>,
  ): FrontendScreenRegistry<TInput>;
}

export interface FrontendComponentRegistry<TInput extends FrontendComponentBuilderMap = FrontendComponentBuilderMap> {
  readonly name: string;
  readonly definitions: FrontendComponentDefinition[];
  readonly ref: {
    readonly [Key in keyof TInput & string]: FrontendComponentRef & { readonly name: Key; readonly key: Key };
  };
}

export interface FrontendScreenRegistry<TInput extends FrontendScreenBuilderMap = FrontendScreenBuilderMap> {
  readonly name: string;
  readonly definitions: FrontendScreenDefinition[];
  readonly ref: {
    readonly [Key in keyof TInput & string]: FrontendScreenRef & { readonly name: Key; readonly key: Key };
  };
}

export interface FrontendBuilder {
  readonly context: FrontendContext;
  readonly schemaComponents: SchemaComponentRegistry[];
  readonly componentRegistries: FrontendComponentRegistry[];
  readonly screenRegistries: FrontendScreenRegistry[];
  readonly components: {
    readonly ref: Record<string, FrontendComponentRef>;
  };
  readonly screens: {
    readonly ref: Record<string, FrontendScreenRef>;
  };
  defineComponents(): FrontendComponentsDefinitionBuilder;
  defineScreens(): FrontendScreensDefinitionBuilder;
  info(info: InfoInput): FrontendBuilder;
}
