export type CliCommand = 'generate' | 'plan' | 'validate' | 'inspect' | 'features' | 'help' | 'version';

export interface CliOptions {
  readonly command: CliCommand;
  readonly projectRoot: string;
  readonly file?: string;
  readonly config?: string;
  readonly task?: string;
  readonly allTasks: boolean;
  readonly dryRun: boolean;
  readonly refresh: boolean;
  readonly skipBefore: boolean;
  readonly skipAfter: boolean;
  readonly json: boolean;
  readonly pretty: boolean;
  readonly verbose: boolean;
}

export interface CliIo {
  readonly stdout: Pick<NodeJS.WriteStream, 'write'>;
  readonly stderr: Pick<NodeJS.WriteStream, 'write'>;
}
