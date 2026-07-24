import path from 'path';
import type { CompilerLogger } from '../logger/compiler-logger.js';
import { PackageOutputFormat } from '../config/package-config.types.js';
import type { OpenApiDocument } from '../openapi/openapi.types.js';
import { createDebugFileName, createOpenApiFileName } from '../output/openapi-file-name.js';
import type { ResolvedOutputConfig } from '../output/output.types.js';
import { sanitizeDebugContract } from '../debug/sanitize-debug-contract.js';
import { writeJsonFile } from './write-json-file.js';
import { writeYamlFile } from './write-yaml-file.js';

export interface WriteOpenApiFilesInput {
  readonly document: OpenApiDocument;
  readonly contractVersion: string;
  readonly contractDebug?: unknown;
  readonly output: ResolvedOutputConfig;
  readonly logger?: CompilerLogger;
}

export function writeOpenApiFiles(input: WriteOpenApiFilesInput): string[] {
  const written: string[] = [];

  input.logger?.detail('Write targets', {
    debugPath: input.output.folder,
    jsonPath: input.output.folder,
    yamlPath: input.output.folder,
    formats: input.output.formats,
  });

  if (input.contractDebug) {
    const debugPath = path.join(input.output.folder, createDebugFileName(input.output.debugFilePrefix, input.contractVersion));

    writeJsonFile(debugPath, sanitizeDebugContract(input.contractDebug));
    written.push(debugPath);
    input.logger?.detail(`Generated ${debugPath}`);
  }

  for (const format of input.output.formats) {
    const filePath = path.join(input.output.folder, createOpenApiFileName(input.output.filePrefix, input.contractVersion, format));

    if (format === PackageOutputFormat.json) {
      writeJsonFile(filePath, input.document);
    }

    if (format === PackageOutputFormat.yaml) {
      writeYamlFile(filePath, input.document);
    }

    written.push(filePath);
    input.logger?.detail(`Generated ${filePath}`);
  }

  return written;
}
