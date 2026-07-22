import type { XCodegenResourceMeta } from '../codegen/codegen-extension.types.js';

export type RuntimeHookPhase = 'beforeValidation' | 'beforeHandler' | 'afterSuccess' | 'afterError' | 'afterSend';

export interface RuntimeTransportSideInbound {
  readonly raw?: boolean;
  readonly ip?: boolean;
  readonly userAgent?: boolean;
  readonly headers?: boolean;
  readonly correlationId?: boolean;
}

export interface RuntimeTransportSideOutbound {
  readonly cookies?: boolean;
  readonly headers?: boolean;
  readonly stream?: boolean;
  readonly bypassSerializer?: boolean;
}

export interface RuntimeTransport {
  readonly inbound?: true | RuntimeTransportSideInbound;
  readonly outbound?: true | RuntimeTransportSideOutbound;
}

export interface RuntimeHookDefinition {
  readonly phase: RuntimeHookPhase;
  readonly transport?: RuntimeTransport;
  readonly description?: string;
}

export interface RuntimeHookOwner {
  readonly resource: XCodegenResourceMeta;
}

export interface RuntimeHookRef<TPhase extends RuntimeHookPhase = RuntimeHookPhase> {
  readonly key: string;
  readonly name: string;
  readonly phase: TPhase;
  readonly owner: RuntimeHookOwner;
  readonly definition: RuntimeHookDefinition & { readonly phase: TPhase };
}

export type RuntimeHookRefMap<TInput extends Record<string, RuntimeHookDefinition>> = {
  readonly [Key in keyof TInput & string]: RuntimeHookRef<TInput[Key]['phase']>;
};

export interface RuntimeHookRegistry<TInput extends Record<string, RuntimeHookDefinition> = Record<string, RuntimeHookDefinition>> {
  readonly owner: RuntimeHookOwner;
  readonly definitions: readonly (RuntimeHookDefinition & { readonly key: keyof TInput & string; readonly owner: RuntimeHookOwner })[];
  readonly ref: RuntimeHookRefMap<TInput>;
}

export type RuntimeHookUsage<TPhase extends RuntimeHookPhase> = RuntimeHookRef<TPhase> | readonly RuntimeHookRef<TPhase>[];

export type RuntimeHookUsageMap = {
  readonly [Phase in RuntimeHookPhase]?: RuntimeHookUsage<Phase>;
};

export interface RuntimeRouteConfig {
  readonly transport?: RuntimeTransport;
  readonly hooks?: RuntimeHookUsageMap;
}
