import type {
  CodepotId,
  ContentDigest,
  JsonObject,
  JsonValue,
} from './common.types';

export const CODEPOT_PROTOCOL_VERSION = 1 as const;
export const CODEPOT_ARTIFACT_VERSION = 1 as const;

export type CodepotProtocolVersion = typeof CODEPOT_PROTOCOL_VERSION;
export type CodepotArtifactVersion = typeof CODEPOT_ARTIFACT_VERSION;

export type ArtifactKind =
  | 'codepot.authoring'
  | 'codepot.templates'
  | 'codepot.template-variables'
  | 'codepot.generation-plan'
  | 'codepot.rendered-generation';

export interface ArtifactProducer {
  readonly name: string;
  readonly version: string;
}

/** Shared deterministic header for persisted Codepot artifacts. */
export interface ArtifactHeader<TKind extends ArtifactKind> {
  readonly kind: TKind;
  readonly protocolVersion: CodepotProtocolVersion;
  readonly artifactVersion: CodepotArtifactVersion;
  readonly producer: ArtifactProducer;
  readonly contentDigest: ContentDigest;
  readonly sourceDigest: ContentDigest;
}

export interface ArtifactReference {
  readonly kind: ArtifactKind;
  readonly contentDigest: ContentDigest;
  readonly sourceDigest: ContentDigest;
}

export interface CompiledDocumentation {
  readonly summary?: string;
  readonly description?: string;
  readonly deprecated?: boolean;
  readonly examples?: readonly JsonValue[];
}

export interface CompiledNamedItem {
  readonly id: CodepotId;
  readonly key: string;
  readonly name: string;
  readonly docs?: CompiledDocumentation;
  readonly metadata?: JsonObject;
}
