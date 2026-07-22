import type {
  CancellationSignal,
  CodepotId,
  JsonObject,
  PortablePath,
} from './common.types';
import type { OperationResult } from './diagnostics.types';
import type { EventBusPort } from './ports.types';
import type {
  AuthoringArtifactLoadRequest,
  AuthoringArtifactLoadResult,
  AuthoringCompileRequest,
  AuthoringCompileResult,
  AuthoringInspectRequest,
  AuthoringInspectResult,
  AuthoringValidateRequest,
  AuthoringValidateResult,
  CodepotFileLoadRequest,
  CodepotFileLoadResult,
  GenerationExecuteRequest,
  GenerationExecuteResult,
  GenerationPlanRequest,
  GenerationPlanResult,
  GenerationRenderRequest,
  GenerationRenderResult,
  GenerationWriteRequest,
  GenerationWriteResult,
  TemplateContextRequest,
  TemplateContextResult,
  TemplateRenderRequest,
  TemplateRenderResult,
  TemplatingCompileRequest,
  TemplatingCompileResult,
  TemplatingValidateRequest,
  TemplatingValidateResult,
} from './requests.types';

export type RuntimeLayer = 'authoring' | 'templating' | 'generation' | 'runtime';

export interface RuntimeFeature {
  readonly id: string;
  readonly version: string;
  readonly layer: RuntimeLayer;
  readonly capabilities: readonly string[];
  readonly metadata?: JsonObject;
}

export interface RuntimeFeatureQuery {
  readonly layer?: RuntimeLayer;
  readonly capability?: string;
}

export interface RuntimeFeatureResult {
  readonly features: readonly RuntimeFeature[];
}

export interface RunContext {
  readonly runId: CodepotId;
  readonly requestId: CodepotId;
  readonly projectRoot?: PortablePath;
  readonly task?: string;
  readonly signal?: CancellationSignal;
  readonly metadata?: JsonObject;
}

export interface RuntimeOperationMap {
  readonly 'authoring.compile': {
    readonly request: AuthoringCompileRequest;
    readonly result: AuthoringCompileResult;
  };
  readonly 'authoring.validate': {
    readonly request: AuthoringValidateRequest;
    readonly result: AuthoringValidateResult;
  };
  readonly 'authoring.inspect': {
    readonly request: AuthoringInspectRequest;
    readonly result: AuthoringInspectResult;
  };
  readonly 'authoring.artifact.load': {
    readonly request: AuthoringArtifactLoadRequest;
    readonly result: AuthoringArtifactLoadResult;
  };
  readonly 'templating.validate': {
    readonly request: TemplatingValidateRequest;
    readonly result: TemplatingValidateResult;
  };
  readonly 'templating.compile': {
    readonly request: TemplatingCompileRequest;
    readonly result: TemplatingCompileResult;
  };
  readonly 'templating.context': {
    readonly request: TemplateContextRequest;
    readonly result: TemplateContextResult;
  };
  readonly 'templating.render': {
    readonly request: TemplateRenderRequest;
    readonly result: TemplateRenderResult;
  };
  readonly 'generation.file.load': {
    readonly request: CodepotFileLoadRequest;
    readonly result: CodepotFileLoadResult;
  };
  readonly 'generation.plan': {
    readonly request: GenerationPlanRequest;
    readonly result: GenerationPlanResult;
  };
  readonly 'generation.render': {
    readonly request: GenerationRenderRequest;
    readonly result: GenerationRenderResult;
  };
  readonly 'generation.write': {
    readonly request: GenerationWriteRequest;
    readonly result: GenerationWriteResult;
  };
  readonly 'generation.execute': {
    readonly request: GenerationExecuteRequest;
    readonly result: GenerationExecuteResult;
  };
  readonly 'runtime.features': {
    readonly request: RuntimeFeatureQuery;
    readonly result: OperationResult<RuntimeFeatureResult>;
  };
}

export type RuntimeOperationKind = keyof RuntimeOperationMap;

export type RuntimeRequest<TKind extends RuntimeOperationKind = RuntimeOperationKind> = {
  readonly [TCurrent in TKind]: {
    readonly kind: TCurrent;
    readonly input: RuntimeOperationMap[TCurrent]['request'];
    readonly context?: Partial<RunContext>;
  };
}[TKind];

export type RuntimeResponse<TKind extends RuntimeOperationKind = RuntimeOperationKind> = {
  readonly [TCurrent in TKind]: {
    readonly kind: TCurrent;
    readonly runId: CodepotId;
    readonly result: RuntimeOperationMap[TCurrent]['result'];
  };
}[TKind];

/** Shared runtime facade consumed by CLI, IDE, UI, and programmatic frontends. */
export interface CodepotRuntimePort {
  readonly events: EventBusPort;

  execute<TKind extends RuntimeOperationKind>(
    request: RuntimeRequest<TKind>,
  ): Promise<RuntimeResponse<TKind>>;

  features(query?: RuntimeFeatureQuery): Promise<RuntimeFeatureResult>;
}
