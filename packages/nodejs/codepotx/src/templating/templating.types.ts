import type {
  CachePort,
  DataCodecPort,
  FileSystemPort,
  HashPort,
  SourceResolverPort,
  TemplateIntrospectionPort,
  TemplatingPort,
} from '@/contract/index';

export type {
  PathsFileInput,
  PathsFolderInput,
  TemplateVariableRequirementInput,
} from './config/paths-input.types';

export interface TemplatingDependencies {
  readonly files: FileSystemPort;
  readonly sources: SourceResolverPort;
  readonly data: DataCodecPort;
  readonly hashes: HashPort;
  readonly cache: CachePort;
}

export interface TemplatingEngine extends TemplatingPort, TemplateIntrospectionPort {}
