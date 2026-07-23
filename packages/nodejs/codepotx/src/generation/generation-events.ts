import type {
  CodepotEvent,
  CommandExecutionOutcome,
  Diagnostic,
  FileWriteOutcome,
} from '@/contract/index';

import type { GenerationDependencies } from './generation.types';

type Draft = CodepotEvent extends infer TEvent
  ? TEvent extends CodepotEvent
    ? Omit<TEvent, 'version' | 'id' | 'runId' | 'sequence' | 'timestamp'>
    : never
  : never;

/**
 * Generation events are observation only. Publishing failures are isolated so
 * frontends and telemetry can never change task control flow.
 */
export class GenerationEventPublisher {
  readonly #dependencies: Pick<GenerationDependencies, 'events' | 'clock' | 'ids'>;
  readonly #runId: string;
  readonly #task: string;
  #sequence = 0;

  constructor(
    dependencies: Pick<GenerationDependencies, 'events' | 'clock' | 'ids'>,
    task = 'generation',
    runId?: string,
  ) {
    this.#dependencies = dependencies;
    this.#task = task;
    this.#runId = runId ?? dependencies.ids.create('generation');
  }

  async stage(
    phase: 'stage.started' | 'stage.completed',
    stage: string,
    payload: { readonly itemCount?: number; readonly durationMs?: number } = {},
  ): Promise<void> {
    await this.#publish({
      source: 'generation',
      type: 'runtime.stage',
      payload: {
        stage,
        message: phase === 'stage.started'
          ? `Starting ${stage}.`
          : `Completed ${stage}.`,
        details: {
          phase,
          task: this.#task,
          ...(payload.itemCount === undefined ? {} : { itemCount: payload.itemCount }),
          ...(payload.durationMs === undefined ? {} : { durationMs: payload.durationMs }),
        },
      },
    });
  }

  async diagnostic(diagnostic: Diagnostic): Promise<void> {
    await this.#publish({
      source: 'generation',
      type: 'diagnostic.published',
      payload: { diagnostic },
    });
  }

  async file(file: FileWriteOutcome): Promise<void> {
    await this.#publish({
      source: 'generation',
      type: 'generation.file.written',
      payload: {
        task: this.#task,
        path: file.path,
        status: file.status,
        ...(file.reason ? { reason: file.reason } : {}),
      },
    });
  }

  async command(command: CommandExecutionOutcome): Promise<void> {
    await this.#publish({
      source: 'generation',
      type: 'generation.command.completed',
      payload: {
        task: this.#task,
        phase: command.phase,
        command: command.command,
        cwd: command.cwd,
        exitCode: command.exitCode,
        optional: command.optional,
      },
    });
  }

  async #publish(event: Draft): Promise<void> {
    this.#sequence += 1;
    try {
      await this.#dependencies.events.publish({
        ...event,
        version: 1,
        id: this.#dependencies.ids.create('event'),
        runId: this.#runId,
        sequence: this.#sequence,
        timestamp: this.#dependencies.clock.now(),
      } as CodepotEvent);
    } catch {
      // Observation must never become hidden control flow.
    }
  }
}
