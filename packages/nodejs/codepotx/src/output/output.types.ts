import type { PackageOutputFormat } from "../config/package-config.types.js";

export interface ResolvedOutputConfig {
  readonly folder: string;
  readonly filePrefix: string;
  readonly debugFilePrefix: string;
  readonly formats: readonly PackageOutputFormat[];
}

export interface OutputFileResult {
  readonly path: string;
  readonly format: PackageOutputFormat;
}
