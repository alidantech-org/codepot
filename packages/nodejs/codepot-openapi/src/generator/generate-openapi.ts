import type { PackageConfig } from '../config/package-config.types.js';
import type { Logger } from '../logging/logger.types.js';
import { resolvePackageConfig } from '../config/resolve-package-config.js';
import { compileOpenApi } from '../compiler/compile-openapi.js';
import { writeOpenApiFiles } from '../writer/write-openapi-files.js';

export interface GenerateOpenApiResult {
  readonly success: boolean;
  readonly files: string[];
  readonly error?: unknown;
}

export async function generateOpenApi(config: PackageConfig, logger?: Logger): Promise<GenerateOpenApiResult> {
  const files: string[] = [];
  const resolvedConfig = resolvePackageConfig(config);

  if (resolvedConfig.contracts.length === 0) {
    return {
      success: false,
      files,
      error: 'No contracts found. Add at least one version contract to package.config.ts.',
    };
  }

  for (const version of resolvedConfig.contracts) {
    const contractTask = logger?.task(`Compiling OpenAPI ${version.contract.info.version}`);
    logger?.info(`Contract: ${version.contract.info.title} ${version.contract.info.version}`);
    logger?.info(`Output: ${resolvedConfig.output.folder}`);

    const compiled = compileOpenApi(version.contract, resolvedConfig.compile);

    if (!compiled.success) {
      contractTask?.fail('Compilation failed');
      return {
        success: false,
        files,
        error: compiled.issues,
      };
    }

    contractTask?.succeed(
      `Compiled OpenAPI ${version.contract.info.version} (${Object.keys(compiled.document?.paths ?? {}).length} paths)`,
    );

    const writeTask = logger?.task('Writing OpenAPI files');
    const writtenFiles = writeOpenApiFiles({
      document: compiled.document,
      contractVersion: version.contract.info.version,
      contractDebug: version.contract,
      output: resolvedConfig.output,
      logger: undefined,
    });
    files.push(...writtenFiles);
    writeTask?.succeed(`Generated ${writtenFiles.length} files`);
  }

  return {
    success: true,
    files,
  };
}
