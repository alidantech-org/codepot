import type {
  CodepotEvent,
  CodepotRuntimePort,
  Diagnostic,
  OperationResult,
  RuntimeFeature,
  RuntimeFeatureQuery,
  RuntimeFeatureResult,
  RuntimeOperationKind,
  RuntimeRequest,
  RuntimeResponse,
  RunContext,
} from '@/contract/index';

import { RunContextStore } from './run-context';
import type { RuntimeDependencies } from './runtime-dependencies.types';

type EventDraft<TEvent extends CodepotEvent = CodepotEvent> = TEvent extends CodepotEvent
  ? Omit<TEvent, 'version' | 'id' | 'runId' | 'sequence' | 'timestamp'>
  : never;

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}

export class CodepotRuntime implements CodepotRuntimePort {
  readonly events: RuntimeDependencies['events'];
  readonly #dependencies: RuntimeDependencies;
  readonly #contexts = new RunContextStore();

  constructor(dependencies: RuntimeDependencies) {
    this.#dependencies = dependencies;
    this.events = dependencies.events;
  }

  async execute<TKind extends RuntimeOperationKind>(
    request: RuntimeRequest<TKind>,
  ): Promise<RuntimeResponse<TKind>> {
    const runId = request.context?.runId ?? this.#dependencies.ids.create('run');
    const context: RunContext = {
      runId,
      requestId: request.context?.requestId ?? this.#dependencies.ids.create('request'),
      ...(request.context?.projectRoot ? { projectRoot: request.context.projectRoot } : {}),
      ...(request.context?.task ? { task: request.context.task } : {}),
      ...(request.context?.signal ? { signal: request.context.signal } : {}),
      ...(request.context?.metadata ? { metadata: request.context.metadata } : {}),
    };
    const startedAt = this.#dependencies.clock.monotonicMilliseconds();
    let sequence = 0;
    const publish = async (event: EventDraft): Promise<void> => {
      sequence += 1;
      try {
        await this.events.publish({
          ...event,
          version: 1,
          id: this.#dependencies.ids.create('event'),
          runId,
          sequence,
          timestamp: this.#dependencies.clock.now(),
        } as CodepotEvent);
      } catch {
        // Events are observational and may not alter required runtime control flow.
      }
    };

    await publish({
      source: 'runtime',
      type: 'runtime.started',
      payload: {
        requestKind: request.kind,
        ...(context.projectRoot ? { projectRoot: context.projectRoot } : {}),
      },
    });

    return this.#contexts.run(context, async () => {
      try {
        context.signal?.throwIfAborted();
        const result = await this.#dispatch(request as unknown as RuntimeRequest);
        context.signal?.throwIfAborted();
        await publish({
          source: 'runtime',
          type: 'runtime.completed',
          payload: {
            requestKind: request.kind,
            success: result.success,
            durationMs: this.#dependencies.clock.monotonicMilliseconds() - startedAt,
          },
        });
        return {
          kind: request.kind,
          runId,
          result,
        } as RuntimeResponse<TKind>;
      } catch (error) {
        const diagnostic: Diagnostic = {
          code: context.signal?.aborted ? 'RUNTIME_CANCELLED' : 'RUNTIME_UNHANDLED_ERROR',
          severity: 'error',
          layer: 'runtime',
          message: errorMessage(error),
        };
        const result: OperationResult<never> = {
          success: false,
          diagnostics: [diagnostic],
        };
        await publish({
          source: 'runtime',
          type: 'runtime.failed',
          payload: {
            requestKind: request.kind,
            durationMs: this.#dependencies.clock.monotonicMilliseconds() - startedAt,
            diagnostics: [diagnostic],
          },
        });
        return {
          kind: request.kind,
          runId,
          result,
        } as RuntimeResponse<TKind>;
      }
    });
  }

  async features(query: RuntimeFeatureQuery = {}): Promise<RuntimeFeatureResult> {
    return {
      features: this.#selectFeatures(query),
    };
  }

  currentContext(): RunContext | undefined {
    return this.#contexts.current();
  }

  async #dispatch(request: RuntimeRequest): Promise<OperationResult<unknown>> {
    switch (request.kind) {
      case 'authoring.compile':
        return this.#dependencies.authoring.compile(request.input as never);
      case 'authoring.validate':
        return this.#dependencies.authoring.validate(request.input as never);
      case 'authoring.inspect':
        return this.#dependencies.authoring.inspect(request.input as never);
      case 'authoring.artifact.load':
        return this.#dependencies.authoring.loadArtifact(request.input as never);
      case 'authoring.cache':
        return this.#dependencies.authoring.cache(request.input as never);
      case 'templating.load':
        return this.#dependencies.templating.load(request.input as never);
      case 'templating.validate':
        return this.#dependencies.templating.validate(request.input as never);
      case 'templating.compile':
        return this.#dependencies.templating.compile(request.input as never);
      case 'templating.context':
        return this.#dependencies.templating.createContext(request.input as never);
      case 'templating.render':
        return this.#dependencies.templating.render(request.input as never);
      case 'generation.file.load':
        return this.#dependencies.generation.load(request.input as never);
      case 'generation.plan':
        return this.#dependencies.generation.plan(request.input as never);
      case 'generation.render':
        return this.#dependencies.generation.render(request.input as never);
      case 'generation.write':
        return this.#dependencies.generation.write(request.input as never);
      case 'generation.clean':
        return this.#dependencies.generation.clean(request.input as never);
      case 'generation.commands':
        return this.#dependencies.generation.runCommands(request.input as never);
      case 'generation.execute':
        return this.#dependencies.generation.execute(request.input as never);
      case 'runtime.features':
        return {
          success: true,
          value: { features: this.#selectFeatures(request.input as RuntimeFeatureQuery) },
          diagnostics: [],
        };
    }
  }

  #selectFeatures(query: RuntimeFeatureQuery): readonly RuntimeFeature[] {
    return (this.#dependencies.features ?? []).filter((feature) => {
      if (query.layer && feature.layer !== query.layer) return false;
      if (query.capability && !feature.capabilities.includes(query.capability)) return false;
      return true;
    });
  }
}
