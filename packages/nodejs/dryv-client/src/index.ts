export const DRYV_API_VERSION = "dryv.api/v1" as const;

export type CacheMode = "use" | "refresh" | "off";
export type WriteKind = "create" | "update" | "unchanged" | "delete_managed";

export interface DryvTransport {
  build(request: DryvBuildRequest): AsyncIterable<DryvBuildEvent>;
  cancel(buildId: string): Promise<void>;
}

export interface DryvResource {
  resourceId: string;
  mediaType: string;
  contentBase64: string;
  contentHash?: string;
}

export interface ProjectPathState {
  path: string;
  exists: boolean;
  contentHash: string | null;
}

export interface ManagedOutput {
  path: string;
  contentHash: string;
  ownershipId: string;
  artifactId: string;
}

export interface DryvBuildRequest {
  apiVersion: typeof DRYV_API_VERSION;
  buildId: string;
  resources: DryvResource[];
  project?: Record<string, unknown>;
  packs: Record<string, unknown>[];
  planningCandidates: Record<string, unknown>[];
  precompiledIrResourceId?: string;
  author?: Record<string, unknown>;
  renderSessionIds?: string[];
  previousManagedOutputs: ManagedOutput[];
  projectSnapshot: ProjectPathState[];
  cacheMode?: CacheMode;
  commitCache?: boolean;
}

export interface ArtifactMetadata {
  artifactId: string;
  path: string;
  logicalOutputId: string;
  contentHash: string;
  ownershipId: string;
  size: number;
  status: "render_complete";
  dependencies: string[];
  provenance: {
    semanticIds: string[];
    packId: string | null;
    selectionKey: string | null;
    templateResourceId: string | null;
    invocationId: string | null;
  };
}

export interface WriteInstruction {
  kind: WriteKind;
  path: string;
  ownershipId: string;
  artifactId: string | null;
  expectedPreviousHash: string | null;
  newContentHash: string | null;
  reason: string;
}

export interface DryvBuildResult {
  apiVersion: typeof DRYV_API_VERSION;
  buildId: string;
  status: "render_complete" | "failed" | "cancelled";
  success: boolean;
  renderComplete: boolean;
  diagnostics: Array<{ code: string; message: string; subject: string | null }>;
  trace: Array<{
    stage: string;
    subject: string;
    message: string;
    details: Record<string, string>;
  }>;
  cache: {
    contextHits: number;
    contextMisses: number;
    renderHits: number;
    renderMisses: number;
  };
  artifacts: ArtifactMetadata[];
  writeInstructions: WriteInstruction[];
  nextManagedOutputs: ManagedOutput[];
}

export type DryvBuildEvent =
  | { type: "build-result"; result: DryvBuildResult }
  | {
      type: "artifact-content";
      artifactId: string;
      offset: number;
      contentBase64: string;
      final: boolean;
    }
  | { type: "stream-complete"; buildId: string; renderComplete: boolean };

export class DryvClient {
  constructor(private readonly transport: DryvTransport) {}

  build(request: DryvBuildRequest): AsyncIterable<DryvBuildEvent> {
    if (request.apiVersion !== DRYV_API_VERSION) {
      throw new Error(`Unsupported Dryv API version: ${request.apiVersion}`);
    }
    if (!request.buildId) throw new Error("Dryv buildId is required");
    return this.transport.build(request);
  }

  cancel(buildId: string): Promise<void> {
    if (!buildId) throw new Error("Dryv buildId is required");
    return this.transport.cancel(buildId);
  }
}
