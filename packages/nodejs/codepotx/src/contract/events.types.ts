import type { ArtifactReference } from './artifact.types';
import type { FileWriteStatus } from './generation-artifact.types';
import type {
  CodepotId,
  IsoTimestamp,
  JsonObject,
  PortablePath,
} from './common.types';
import type { Diagnostic, DiagnosticLayer } from './diagnostics.types';

export interface EventEnvelope<TType extends string, TPayload> {
  readonly version: 1;
  readonly id: CodepotId;
  readonly runId: CodepotId;
  readonly sequence: number;
  readonly timestamp: IsoTimestamp;
  readonly source: DiagnosticLayer;
  readonly type: TType;
  readonly payload: TPayload;
}

export interface RuntimeStartedPayload {
  readonly requestKind: string;
  readonly projectRoot?: PortablePath;
}

export interface RuntimeCompletedPayload {
  readonly requestKind: string;
  readonly success: boolean;
  readonly durationMs: number;
}

export interface RuntimeFailedPayload {
  readonly requestKind: string;
  readonly durationMs: number;
  readonly diagnostics: readonly Diagnostic[];
}

export interface StagePayload {
  readonly stage: string;
  readonly message: string;
  readonly current?: number;
  readonly total?: number;
  readonly details?: JsonObject;
}

export interface SourceResolvedPayload {
  readonly sourceId: CodepotId;
  readonly root: PortablePath;
  readonly entry: PortablePath;
  readonly digest: string;
}

export interface ArtifactCreatedPayload {
  readonly artifact: ArtifactReference;
  readonly itemCount?: number;
}

export interface GenerationTaskPayload {
  readonly task: string;
}

export interface GenerationPlanPayload extends GenerationTaskPayload {
  readonly plan: ArtifactReference;
  readonly fileCount: number;
}

export interface FileLifecyclePayload extends GenerationTaskPayload {
  readonly path: PortablePath;
  readonly status: FileWriteStatus | 'rendered';
  readonly reason?: string;
}

export interface CommandLifecyclePayload extends GenerationTaskPayload {
  readonly phase: 'before' | 'after';
  readonly command: string;
  readonly cwd: PortablePath;
  readonly exitCode?: number | null;
  readonly optional: boolean;
}

export interface DiagnosticPublishedPayload {
  readonly diagnostic: Diagnostic;
}

export type CodepotEvent =
  | EventEnvelope<'runtime.started', RuntimeStartedPayload>
  | EventEnvelope<'runtime.completed', RuntimeCompletedPayload>
  | EventEnvelope<'runtime.failed', RuntimeFailedPayload>
  | EventEnvelope<'runtime.stage', StagePayload>
  | EventEnvelope<'authoring.source.resolved', SourceResolvedPayload>
  | EventEnvelope<'authoring.compiled', ArtifactCreatedPayload>
  | EventEnvelope<'templating.source.resolved', SourceResolvedPayload>
  | EventEnvelope<'templating.compiled', ArtifactCreatedPayload>
  | EventEnvelope<'generation.task.started', GenerationTaskPayload>
  | EventEnvelope<'generation.plan.created', GenerationPlanPayload>
  | EventEnvelope<'generation.file.rendered', FileLifecyclePayload>
  | EventEnvelope<'generation.file.written', FileLifecyclePayload>
  | EventEnvelope<'generation.command.started', CommandLifecyclePayload>
  | EventEnvelope<'generation.command.completed', CommandLifecyclePayload>
  | EventEnvelope<'diagnostic.published', DiagnosticPublishedPayload>;

export type CodepotEventType = CodepotEvent['type'];

export type CodepotEventOf<TType extends CodepotEventType> = Extract<
  CodepotEvent,
  { readonly type: TType }
>;

export type CodepotEventListener<TEvent extends CodepotEvent = CodepotEvent> = (
  event: TEvent,
) => void | Promise<void>;
