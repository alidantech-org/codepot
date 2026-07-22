import { createRequire } from 'node:module';
import { readFile } from 'node:fs/promises';
import { spawn } from 'node:child_process';
import { writeFile, mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import type { CompilerLogger } from '../logger/compiler-logger.js';
import type { OpenApiDocument } from '../openapi/openapi.types.js';
import type { OpenApiValidationConfig } from '../config/package-config.types.js';

const require = createRequire(import.meta.url);

interface RedoclyPackageJson {
  readonly bin?: string | Record<string, string>;
}

async function resolveRedoclyBin(): Promise<string> {
  const packageJsonPath = require.resolve('@redocly/cli/package.json');
  const packageDir = dirname(packageJsonPath);

  const rawPackageJson = await readFile(packageJsonPath, 'utf-8');
  const redoclyPackageJson = JSON.parse(rawPackageJson) as RedoclyPackageJson;

  const binRelative =
    typeof redoclyPackageJson.bin === 'string'
      ? redoclyPackageJson.bin
      : (redoclyPackageJson.bin?.redocly ?? redoclyPackageJson.bin?.['redocly-cli']);

  if (!binRelative) {
    throw new Error('Could not resolve @redocly/cli binary.');
  }

  return join(packageDir, binRelative);
}

export interface OpenApiValidationResult {
  readonly valid: boolean;
  readonly errors: readonly string[];
  readonly warnings: readonly string[];
  readonly output?: string;
}

export async function validateOpenApiDocument(
  document: OpenApiDocument,
  config: OpenApiValidationConfig = {},
): Promise<OpenApiValidationResult> {
  const tempDir = await mkdtemp(join(tmpdir(), 'codepot-openapi-'));

  try {
    // Write document to temp file
    const docPath = join(tempDir, 'openapi.json');
    await writeFile(docPath, JSON.stringify(document, null, 2), 'utf-8');

    // Create Redocly config
    const configPath = join(tempDir, 'redocly.yaml');
    const noUnusedComponentsRule = config.allowUnusedComponents === false ? (config.failOnWarnings === true ? 'error' : 'warn') : 'off';
    const redoclyConfig = ['extends:', '  - recommended', 'rules:', `  no-unused-components: ${noUnusedComponentsRule}`, ''].join('\n');
    await writeFile(configPath, redoclyConfig, 'utf-8');

    // Run Redocly lint
    const result = await runRedoclyLint(docPath, configPath, config);

    if (!result.valid) {
      return {
        valid: false,
        errors: result.errors,
        warnings: result.warnings,
        output: result.output,
      };
    }

    return {
      valid: true,
      errors: [],
      warnings: result.warnings ?? [],
      output: result.output,
    };
  } finally {
    // Cleanup temp directory
    await rm(tempDir, { recursive: true, force: true }).catch(() => {});
  }
}

export async function validateOpenApiFile(
  filePath: string,
  config: OpenApiValidationConfig = {},
  logger?: CompilerLogger,
): Promise<OpenApiValidationResult> {
  const validationLogger = logger?.child({ scope: 'validation' });

  validationLogger?.detail('Validation config', {
    allowUnusedComponents: config.allowUnusedComponents,
    failOnWarnings: config.failOnWarnings,
  });

  const tempDir = await mkdtemp(join(tmpdir(), 'codepot-openapi-'));

  try {
    logger?.verbose('Running Redocly validation', {
      filePath,
      allowUnusedComponents: config.allowUnusedComponents,
      failOnWarnings: config.failOnWarnings,
    });

    // Create Redocly config
    const configPath = join(tempDir, 'redocly.yaml');
    const noUnusedComponentsRule = config.allowUnusedComponents === false ? (config.failOnWarnings === true ? 'error' : 'warn') : 'off';
    const redoclyConfig = ['extends:', '  - recommended', 'rules:', `  no-unused-components: ${noUnusedComponentsRule}`, ''].join('\n');

    logger?.debug('Generated Redocly config', redoclyConfig);

    logger?.trace('Redocly config', redoclyConfig);

    await writeFile(configPath, redoclyConfig, 'utf-8');

    // Run Redocly lint on actual file
    const result = await runRedoclyLint(filePath, configPath, config, logger);

    if (!result.valid) {
      return {
        valid: false,
        errors: result.errors,
        warnings: result.warnings,
        output: result.output,
      };
    }

    return {
      valid: true,
      errors: [],
      warnings: result.warnings ?? [],
      output: result.output,
    };
  } finally {
    // Cleanup temp directory
    await rm(tempDir, { recursive: true, force: true }).catch(() => {});
  }
}

async function runRedoclyLint(
  docPath: string,
  configPath: string,
  validationConfig: OpenApiValidationConfig,
  logger?: CompilerLogger,
): Promise<{ valid: boolean; errors: string[]; warnings: string[]; output: string }> {
  const redoclyBin = await resolveRedoclyBin();

  return new Promise((resolve) => {
    const redocly = spawn(process.execPath, [redoclyBin, 'lint', docPath, '--config', configPath], {
      cwd: process.cwd(),
      stdio: ['ignore', 'pipe', 'pipe'],
      shell: false,
    });

    let stdout = '';
    let stderr = '';

    redocly.stdout.on('data', (data: Buffer) => {
      stdout += data.toString();
    });

    redocly.stderr.on('data', (data: Buffer) => {
      stderr += data.toString();
    });

    redocly.on('close', (code: number | null) => {
      const combinedOutput = [stdout, stderr].filter(Boolean).join('\n').trim();

      // Detect Redocly internal/config errors
      const isRedoclyProcessingError =
        combinedOutput.includes('Something went wrong') ||
        combinedOutput.includes('config?.') ||
        combinedOutput.includes('is not a function');

      if (isRedoclyProcessingError) {
        resolve({ valid: false, errors: [combinedOutput], warnings: [], output: combinedOutput });
        return;
      }

      if (code === 0) {
        resolve({ valid: true, errors: [], warnings: [], output: combinedOutput });
      } else {
        // If failOnWarnings is true, any non-zero exit is an error
        if (validationConfig.failOnWarnings === true) {
          resolve({ valid: false, errors: [combinedOutput || `Redocly exited with code ${code}`], warnings: [], output: combinedOutput });
        } else {
          // Otherwise, treat as warnings unless it's a critical error
          const hasErrors = stderr.toLowerCase().includes('error') && !stderr.toLowerCase().includes('no-unused-components');
          if (hasErrors) {
            resolve({ valid: false, errors: [combinedOutput || `Redocly exited with code ${code}`], warnings: [], output: combinedOutput });
          } else {
            resolve({ valid: true, errors: [], warnings: [combinedOutput], output: combinedOutput });
          }
        }
      }
    });

    redocly.on('error', (error: Error) => {
      resolve({ valid: false, errors: [error.message], warnings: [], output: error.message });
    });
  });
}
