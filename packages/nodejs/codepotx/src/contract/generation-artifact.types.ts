import type { ArtifactHeader, ArtifactReference } from './artifact.types';
import type {
  CodepotId,
  ContentDigest,
  JsonObject,
  PortablePath,
} from './common.types';
import type { Diagnostic } from './diagnostics.types';
import type {
  FileCompareMode,
  FileLifecycleMode,
} from './template-artifact.types';

export interface PlannedDependency {
  readonly ref: CodepotId;
  readonly purpose: string;
  readonly targetRef?: CodepotId;
  readonly outputPath?: PortablePath;
  readonly importPath?: string;
  readonly metadata?: JsonObject;
}

export interface PlannedFile {
  readonly id: CodepotId;
  readonly templateId: CodepotId;
  readonly outputPath: PortablePath;
  readonly group: string;
  readonly lifecycle: FileLifecycleMode;
  readonly compareMode: FileCompareMode;
  readonly context: JsonObject;
  readonly dependencies: readonly PlannedDependency[];
  readonly refusalReason?: string;
}

export interface PlannedCommand {
  readonly id: CodepotId;
  readonly phase: 'before' | 'after';
  readonly name?: string;
  readonly command: string;
  readonly cwd: PortablePath;
  readonly optional: boolean;
  readonly environment: Readonly<Record<string, string>>;
}

export interface PlannedCleanOperation {
  readonly id: CodepotId;
  readonly path: PortablePath;
  readonly allowed: boolean;
  readonly refusalReason?: string;
}

/** Deterministic plan created before template rendering or filesystem writes. */
export interface GenerationPlan {
  readonly header: ArtifactHeader<'codepot.generation-plan'>;
  readonly task: string;
  readonly projectRoot: PortablePath;
  readonly outputRoot: PortablePath;
  readonly authoring: ArtifactReference;
  readonly templates: ArtifactReference;
  readonly files: readonly PlannedFile[];
  readonly commands: readonly PlannedCommand[];
  readonly clean: readonly PlannedCleanOperation[];
  readonly diagnostics: readonly Diagnostic[];
}

export interface Utf8VirtualFileContent {
  readonly encoding: 'utf8';
  readonly text: string;
}

export interface Base64VirtualFileContent {
  readonly encoding: 'base64';
  readonly data: string;
}

export type VirtualFileContent = Utf8VirtualFileContent | Base64VirtualFileContent;

export interface VirtualFile {
  readonly id: CodepotId;
  readonly path: PortablePath;
  readonly lifecycle: FileLifecycleMode;
  readonly compareMode: FileCompareMode;
  readonly content: VirtualFileContent;
  readonly contentDigest: ContentDigest;
  readonly metadata?: JsonObject;
}

/** In-memory rendered output before any writer is selected. */
export interface RenderedGeneration {
  readonly header: ArtifactHeader<'codepot.rendered-generation'>;
  readonly plan: ArtifactReference;
  readonly files: readonly VirtualFile[];
  readonly diagnostics: readonly Diagnostic[];
}

export type FileWriteStatus =
  | 'created'
  | 'updated'
  | 'unchanged'
  | 'skipped'
  | 'refused';

export interface FileWriteOutcome {
  readonly path: PortablePath;
  readonly status: FileWriteStatus;
  readonly lifecycle: FileLifecycleMode;
  readonly reason?: string;
}

export interface CommandExecutionOutcome {
  readonly id: CodepotId;
  readonly phase: 'before' | 'after';
  readonly command: string;
  readonly cwd: PortablePath;
  readonly exitCode: number | null;
  readonly skipped: boolean;
  readonly optional: boolean;
  readonly stdout: string;
  readonly stderr: string;
}

export interface GenerationResult {
  readonly task: string;
  readonly dryRun: boolean;
  readonly plan: GenerationPlan;
  readonly rendered: RenderedGeneration;
  readonly files: readonly FileWriteOutcome[];
  readonly commands: readonly CommandExecutionOutcome[];
  readonly cleaned: readonly PortablePath[];
  readonly diagnostics: readonly Diagnostic[];
}
