import type { CodepotEvent } from 'codepotx/contract';

import { parseCliArguments } from './args';
import { executeCliCommand } from './commands';
import type { CliIo, CliOptions } from './cli.types';
import { CliPresenter } from './presenter';
import { loadProjectRuntime } from './runtime-loader';

export async function runCli(
  argv: readonly string[] = process.argv.slice(2),
  io: CliIo = { stdout: process.stdout, stderr: process.stderr },
): Promise<number> {
  let options: CliOptions;
  try {
    options = parseCliArguments(argv);
  } catch (caught) {
    return new CliPresenter({ command: 'help', projectRoot: process.cwd(), allTasks: false, dryRun: false, refresh: false, skipBefore: false, skipAfter: false, json: false, pretty: true, verbose: false }, io).error(caught);
  }
  const presenter = new CliPresenter(options, io);
  if (options.command === 'help' || options.command === 'version') {
    const value = await executeCliCommand({} as never, options);
    presenter.text(String(value));
    return 0;
  }
  try {
    const runtime = await loadProjectRuntime(options.projectRoot);
    const subscription = runtime.events.subscribe((event: CodepotEvent) => presenter.event(event));
    try {
      const result = await executeCliCommand(runtime, options);
      return typeof result === 'string' ? (presenter.text(result), 0) : presenter.result(result);
    } finally {
      await subscription.dispose();
    }
  } catch (caught) {
    return presenter.error(caught);
  }
}
