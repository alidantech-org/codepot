import type {
  CachePort,
  DataCodecPort,
  FileSystemPort,
  HashPort,
  JsonObject,
  JsonValue,
  SourceResolverPort,
  TemplateIntrospectionPort,
  TemplateVariableKind,
  TemplatingPort,
} from '@/contract/index';

export interface TemplatingDependencies {
  readonly files: FileSystemPort;
  readonly sources: SourceResolverPort;
  readonly data: DataCodecPort;
  readonly hashes: HashPort;
  readonly cache: CachePort;
}

export interface TemplatingEngine extends TemplatingPort, TemplateIntrospectionPort {}

export interface TemplateVariableRequirementInput {
  readonly path: string;
  readonly required?: boolean;
  readonly kind?: TemplateVariableKind;
  readonly description?: string;
}

export interface PathsFolderInput {
  readonly parts?: readonly JsonValue[];
  readonly select?: string;
  readonly as?: string;
  readonly alias?: string;
  readonly mode?: 'each' | 'group' | 'once';
  readonly lifecycle?: 'managed' | 'immutable';
  readonly description?: string;
  readonly metadata?: JsonObject;
}

export interface PathsFileInput {
  readonly name?: string;
  readonly version?: string;
  readonly description?: string;
  readonly templateExtension?: string;
  readonly template_extension?: string;
  readonly stripTemplateExtension?: boolean;
  readonly strip_template_extension?: boolean;
  readonly allowRawFiles?: boolean;
  readonly allow_raw_files?: boolean;
  readonly includeHidden?: boolean;
  readonly include_hidden?: boolean;
  readonly ignore?: readonly string[];
  readonly helpers?: readonly string[];
  readonly partials?: readonly string[];
  readonly variables?: readonly TemplateVariableRequirementInput[] | {
    readonly required?: readonly (string | TemplateVariableRequirementInput)[];
    readonly optional?: readonly (string | TemplateVariableRequirementInput)[];
  };
  readonly metadata?: JsonObject;
  readonly folders?: Readonly<Record<string, PathsFolderInput>>;
  readonly write?: {
    readonly defaultMode?: 'managed' | 'immutable';
    readonly default_mode?: 'managed' | 'immutable';
    readonly managedRoots?: readonly string[];
    readonly managed_roots?: readonly string[];
    readonly immutableRoots?: readonly string[];
    readonly immutable_roots?: readonly string[];
    readonly protectedRoots?: readonly string[];
    readonly protected_roots?: readonly string[];
    readonly cleanRoots?: readonly string[];
    readonly clean_roots?: readonly string[];
  };
}
