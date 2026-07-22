import type { CommandRequest, CommandResult, CommandRunnerPort } from '@/contract/index';

export type MemoryCommandHandler = (request: CommandRequest) => Promise<CommandResult> | CommandResult;

export class MemoryCommandRunner implements CommandRunnerPort {
  readonly requests: CommandRequest[] = [];
  readonly #handler: MemoryCommandHandler;

  constructor(handler?: MemoryCommandHandler) {
    this.#handler = handler ?? ((request) => ({
      command: request.command,
      cwd: request.cwd,
      exitCode: request.dryRun ? null : 0,
      stdout: '',
      stderr: '',
      skipped: request.dryRun ?? false,
    }));
  }

  async run(request: CommandRequest): Promise<CommandResult> {
    request.signal?.throwIfAborted();
    this.requests.push(request);
    const result = await this.#handler(request);
    request.signal?.throwIfAborted();
    return result;
  }
}
