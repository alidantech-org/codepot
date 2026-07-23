import type {
  CodepotId,
  CodepotRuntimePort,
  Diagnostic,
  OperationFailure,
  RuntimeFeatureQuery,
  RuntimeFeatureResult,
  RuntimeOperationKind,
  RuntimeOperationMap,
  RuntimeRequest,
  RuntimeResponse,
  RunContext,
} from '@/contract/index';
import { createRunContext, RunContextStore } from './context/index';
import {
  createRuntimeOperationHandlers,
  dispatchRuntimeOperation,
  selectRuntimeFeatures,
} from './dispatch/index';
import type { RuntimeOperationHandlerRegistry } from './dispatch/index';
import type { RuntimeDependencies } from './runtime-dependencies.types';
import { RuntimeEventPublisher } from './runtime-event-publisher';

export class CodepotRuntime implements CodepotRuntimePort {
  readonly events: RuntimeDependencies['events'];
  readonly #dependencies: RuntimeDependencies;
  readonly #contexts: RunContextStore;
  readonly #handlers: RuntimeOperationHandlerRegistry;

  constructor(dependencies: RuntimeDependencies) {
    this.#dependencies = dependencies;
    this.events = dependencies.events;
    this.#contexts = new RunContextStore();
    this.#handlers = createRuntimeOperationHandlers(dependencies);
  }

  async execute<TKind extends RuntimeOperationKind>(
    request: RuntimeRequest<TKind>,
  ): Promise<RuntimeResponse<TKind>> {
    const context = createRunContext(this.#dependencies, request.context);
    const startedAt = this.#dependencies.clock.monotonicMilliseconds();
    const events = new RuntimeEventPublisher(this.#dependencies, context.runId);

    await events.started(request.kind, context.projectRoot);
    return this.#contexts.run(context, async () => {
      try {
        context.signal?.throwIfAborted();
        const result = await dispatchRuntimeOperation(
          this.#handlers,
          request.kind,
          request.input,
          context,
        );
        context.signal?.throwIfAborted();
        await events.completed(
          request.kind,
          result.success,
          this.#dependencies.clock.monotonicMilliseconds() - startedAt,
        );
        return createRuntimeResponse(request.kind, context.runId, result);
      } catch (caught) {
        const diagnostic: Diagnostic = {
          code: context.signal?.aborted ? 'RUNTIME_CANCELLED' : 'RUNTIME_UNHANDLED_ERROR',
          severity: 'error',
          layer: 'runtime',
          message: caught instanceof Error ? caught.message : String(caught),
        };
        const result: OperationFailure = { success: false, diagnostics: [diagnostic] };
        await events.failed(
          request.kind,
          this.#dependencies.clock.monotonicMilliseconds() - startedAt,
          result.diagnostics,
        );
        return createRuntimeResponse(request.kind, context.runId, result);
      }
    });
  }

  async features(query: RuntimeFeatureQuery = {}): Promise<RuntimeFeatureResult> {
    return {
      features: selectRuntimeFeatures(this.#dependencies.features ?? [], query),
    };
  }

  currentContext(): RunContext | undefined {
    return this.#contexts.current();
  }
}

function createRuntimeResponse<TKind extends RuntimeOperationKind>(
  kind: TKind,
  runId: CodepotId,
  result: RuntimeOperationMap[TKind]['result'],
): RuntimeResponse<TKind> {
  return { kind, runId, result };
}
