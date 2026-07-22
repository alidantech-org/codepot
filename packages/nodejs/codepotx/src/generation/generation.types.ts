import type {
  AuthoringPort,
  CachePort,
  ClockPort,
  CommandRunnerPort,
  DataCodecPort,
  EventBusPort,
  FileSystemPort,
  FileWriterPort,
  GenerationPort,
  HashPort,
  IdPort,
  JsonObject,
  JsonValue,
  SourceDescriptor,
  SourceResolverPort,
  TemplateIntrospectionPort,
  TemplatingPort,
} from '@/contract/index';

import type { GenerationImportAdapter } from './imports.types';

export interface GenerationDependencies {
  readonly authoring: AuthoringPort;
  readonly templating: TemplatingPort & TemplateIntrospectionPort;
  readonly files: FileSystemPort;
  readonly writer: FileWriterPort;
  readonly data: DataCodecPort;
  readonly sources: SourceResolverPort;
  readonly commands: CommandRunnerPort;
  readonly hashes: HashPort;
  readonly cache: CachePort;
  readonly ids: IdPort;
  readonly clock: ClockPort;
  readonly events: EventBusPort;
  readonly imports?: GenerationImportAdapter | undefined;
}

export interface GenerationEngine extends GenerationPort {}

export interface CodepotFileInput {
  readonly allow?: boolean;
  readonly defaults?: JsonObject;
  readonly sources?: Readonly<Record<string, SourceInput>>;
  readonly tasks?: Readonly<Record<string, CodepotTaskInput>> | readonly CodepotTaskInput[];
}

export type SourceInput = string | SourceDescriptor | {
  readonly type?: SourceDescriptor['kind'];
  readonly kind?: SourceDescriptor['kind'];
  readonly path?: string;
  readonly entry?: string;
  readonly package?: string;
  readonly version?: string;
  readonly repository?: string;
  readonly ref?: string;
  readonly id?: string;
};

export interface CodepotCommandInput {
  readonly name?: string;
  readonly run: string;
  readonly cwd?: string;
  readonly optional?: boolean;
  readonly environment?: Readonly<Record<string, string>>;
  readonly env?: Readonly<Record<string, string>>;
}

export interface CodepotTaskInput {
  readonly name?: string;
  readonly description?: string;
  readonly authoring?: SourceInput;
  readonly templates?: SourceInput;
  readonly input?: string;
  readonly template_dir?: string;
  readonly output?: string;
  readonly clean?: readonly string[];
  readonly before?: readonly CodepotCommandInput[];
  readonly after?: readonly CodepotCommandInput[];
  readonly environment?: Readonly<Record<string, string>>;
  readonly env?: Readonly<Record<string, string>>;
  readonly variables?: JsonObject;
  readonly frontend?: string;
  readonly transactional?: boolean;
  readonly manifest?: string;
}

export interface SelectionContext extends Record<string, unknown> {
  readonly authoring: JsonObject;
  readonly project: JsonObject;
  readonly variables: JsonObject;
}

export type SelectionValue = JsonValue | readonly JsonValue[];
