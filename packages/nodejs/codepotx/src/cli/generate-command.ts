import { loggerConfigFromCliArgs, type ParsedCliArgs } from './cli-args.js';
import { createLogger } from '../logging/create-logger.js';
import { LogLevel } from '../logging/log-level.js';
import { CliMessage } from './cli.constants.js';
import { loadPackageConfig } from './load-package-config.js';
import { OpenApiTs } from '../index.js';

export async function runGenerateCommand(args: ParsedCliArgs): Promise<number> {
  const cliLoggerConfig = loggerConfigFromCliArgs(args);
  const bootstrapLogger = createLogger({ level: LogLevel.silent });

  const config = await loadPackageConfig();

  const logger = createLogger({ level: cliLoggerConfig.level ?? LogLevel.normal });

  const api = new OpenApiTs();

  try {
    const result = await api.generate({ config, logger });

    if (!result.success) {
      logger.error('Generation failed');
      console.error(result.error);
      return 1;
    }

    for (const file of result.files) {
      console.log(CliMessage.generated(file));
    }

    console.log(CliMessage.done);
    return 0;
  } catch (error) {
    logger.error('Generation failed');
    console.error(CliMessage.failed, error);
    return 1;
  }
}
