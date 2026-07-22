/**
 * File Pattern Utilities
 *
 * Utilities for classifying file paths based on patterns.
 * Used by the watch classifier to determine file change types.
 */

/**
 * Utility class for file pattern matching.
 */
export class FilePatternUtils {
  /**
   * Check if a path matches global config file patterns.
   *
   * Global config files are typically in the root or .codepurify directory
   * and contain project-wide configuration.
   */
  static isGlobalConfig(path: string): boolean {
    // Convert to POSIX path for consistent matching
    const posixPath = path.replace(/\\/g, '/');

    // Check for common global config patterns
    const globalConfigPatterns = [
      /^codepurify\.config\.(ts|js|mjs)$/,
      /^\.codepurify\/config\.(ts|js|mjs)$/,
      /^\.codepurify\/templates\.(ts|js|mjs)$/,
      /^tempurify\.config\.(ts|js|mjs)$/,
      /^tempurify\.(ts|js|mjs)$/,
    ];

    return globalConfigPatterns.some((pattern) => pattern.test(posixPath));
  }

  /**
   * Check if a path matches template registry file patterns.
   *
   * Template registry files contain template definitions and registrations.
   */
  static isTemplateRegistry(path: string): boolean {
    // Convert to POSIX path for consistent matching
    const posixPath = path.replace(/\\/g, '/');

    // Check for template registry patterns
    const templateRegistryPatterns = [
      /^templates\.(ts|js|mjs)$/,
      /^\.codepurify\/templates\.(ts|js|mjs)$/,
      /^src\/templates\/.*\.(ts|js|mjs)$/,
      /^templates\/.*\.(ts|js|mts)$/,
    ];

    return templateRegistryPatterns.some((pattern) => pattern.test(posixPath));
  }

  /**
   * Check if a path matches entity config file patterns.
   *
   * Entity config files are user-owned configuration files for specific entities.
   */
  static isEntityConfig(path: string): boolean {
    // Convert to POSIX path for consistent matching
    const posixPath = path.replace(/\\/g, '/');

    // Check for entity config patterns
    const entityConfigPatterns = [
      /^src\/[^/]+\/[^/]+\/[^/]+\.config\.(ts|js|mjs)$/,
      /^types\/[^/]+\/[^/]+\/[^/]+\.config\.(ts|js|mjs)$/,
      /\/config\/[^/]+\/[^/]+\.config\.(ts|js|mjs)$/,
      /\.config\.(ts|js|mjs)$/,
    ];

    return entityConfigPatterns.some((pattern) => pattern.test(posixPath));
  }
}
