import type { ArtifactHeader } from '../../protocol/artifact.types';
import type {
  CodepotId,
  ContentDigest,
  JsonObject,
  JsonValue,
  PortablePath,
} from '../../protocol/common.types';
import type { Diagnostic } from '../../diagnostics/diagnostic.types';
import type { ResolvedSource, SourceFileReference } from '../../sources/source.types';
import type {
  TemplateReference,
  TemplateVariableRequirement,
} from './template-variables.types';

export type TemplateSelectionMode = 'each' | 'group' | 'once';
export type FileLifecycleMode = 'managed' | 'immutable';
export type FileCompareMode = 'exact' | 'layoutInsensitive' | 'raw';

export interface CompiledPathToken {
  readonly kind: 'folder' | 'dynamic' | 'escapedFolder' | 'escapedDynamic' | 'static';
  readonly raw: string;
  readonly expression?: string;
}

export interface CompiledTemplateFolder {
  readonly name: string;
  readonly parts: readonly JsonValue[];
  readonly select?: string;
  readonly alias?: string;
  readonly mode: TemplateSelectionMode;
  readonly lifecycle?: FileLifecycleMode | undefined;
  readonly description?: string;
  readonly metadata?: JsonObject;
}

export interface CompiledWritePolicy {
  readonly defaultMode: FileLifecycleMode;
  readonly managedRoots: readonly PortablePath[];
  readonly immutableRoots: readonly PortablePath[];
  readonly protectedRoots: readonly PortablePath[];
  readonly cleanRoots: readonly PortablePath[];
}

export interface CompiledTemplateDescriptor {
  readonly id: CodepotId;
  readonly path: PortablePath;
  readonly kind: 'handlebars' | 'partial' | 'raw';
  readonly group: string;
  readonly outputTokens: readonly CompiledPathToken[];
  readonly partialName?: string;
  readonly lifecycle?: FileLifecycleMode | undefined;
  readonly compareMode: FileCompareMode;
  readonly references: readonly TemplateReference[];
  readonly text?: string;
  readonly dataBase64?: string;
  readonly digest: ContentDigest;
  readonly metadata?: JsonObject;
}

export interface TemplatePackManifest {
  readonly name: string;
  readonly version: string;
  readonly description?: string;
  readonly templateExtension: string;
  readonly stripTemplateExtension: boolean;
  readonly allowRawFiles: boolean;
  readonly includeHidden: boolean;
  readonly ignore: readonly string[];
  readonly helpers: readonly string[];
  readonly partials: readonly string[];
  readonly variableRequirements: readonly TemplateVariableRequirement[];
  readonly metadata?: JsonObject;
}

/** Validated serializable representation of paths.yaml and template sources. */
export interface CompiledTemplatePack {
  readonly header: ArtifactHeader<'codepot.templates'>;
  readonly source: ResolvedSource;
  readonly manifest: TemplatePackManifest;
  readonly folders: readonly CompiledTemplateFolder[];
  readonly writePolicy: CompiledWritePolicy;
  readonly templates: readonly CompiledTemplateDescriptor[];
  readonly files: readonly SourceFileReference[];
  readonly diagnostics: readonly Diagnostic[];
}
