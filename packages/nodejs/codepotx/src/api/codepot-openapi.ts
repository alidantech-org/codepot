import fs from 'fs';
import path from 'path';
import { generateOpenApi } from '../generator/generate-openapi.js';
import type { GenerateInput, GenerateResult, InitConfigInput, InitConfigResult, OpenApiTsApi } from './codepot-openapi.types.js';

const DefaultConfigFileName = 'package.config.ts';

export class OpenApiTs implements OpenApiTsApi {
  async initConfig(input: InitConfigInput = {}): Promise<InitConfigResult> {
    const cwd = input.cwd ?? process.cwd();
    const fileName = input.fileName ?? DefaultConfigFileName;
    const filePath = path.join(cwd, fileName);

    if (fs.existsSync(filePath) && !input.force) {
      return {
        success: true,
        filePath,
        skipped: true,
      };
    }

    try {
      fs.writeFileSync(filePath, createDefaultConfig(), 'utf-8');

      return {
        success: true,
        filePath,
      };
    } catch (error) {
      return {
        success: false,
        error,
      };
    }
  }

  async generate(input: GenerateInput): Promise<GenerateResult> {
    return generateOpenApi(input.config, input.logger);
  }
}

function createDefaultConfig(): string {
  return [
    "import { definePackageConfig } from 'codepot-openapi';",
    '',
    'export default definePackageConfig({',
    '  contracts: [],',
    '});',
    '',
  ].join('\n');
}
