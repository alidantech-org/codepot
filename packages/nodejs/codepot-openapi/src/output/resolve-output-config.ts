import type { PackageOutputConfig } from "../config/package-config.types.js";
import { DefaultOutputConfig } from "./output.constants.js";
import type { ResolvedOutputConfig } from "./output.types.js";

export function resolveOutputConfig(
  config?: Partial<PackageOutputConfig>,
): ResolvedOutputConfig {
  return {
    folder: config?.folder ?? DefaultOutputConfig.folder,
    filePrefix: config?.filePrefix ?? DefaultOutputConfig.filePrefix,
    debugFilePrefix:
      config?.debugFilePrefix ?? DefaultOutputConfig.debugFilePrefix,
    formats: config?.formats ?? DefaultOutputConfig.formats,
  };
}
