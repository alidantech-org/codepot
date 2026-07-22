/**
 * codepot Config Definition Helper
 *
 * Provides the definecodepotConfig helper function for users to define
 * their codepot configuration with type safety and validation.
 */

import { codepotConfig } from '../types/codepot.config.types';

/**
 * Helper function to define codepot configuration
 *
 * This function provides type safety and validation for user-defined
 * codepot configuration. It can be used in config files like:
 *
 * ```js
 * const { definecodepotConfig } = require("codepot");
 *
 * module.exports = definecodepotConfig({
 *   project: {
 *     name: "my-app"
 *   }
 * });
 * ```
 *
 * @param config - User configuration object
 * @returns Enhanced configuration object with template filtering methods
 */
export function definecodepotConfig(config: codepotConfig): codepotConfig {
  // Basic validation to ensure config is an object
  if (typeof config !== 'object' || config === null) {
    throw new Error('codepot config must be an object');
  }

  return config;
}
