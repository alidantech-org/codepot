/**
 * Codepurify Config Definition Helper
 *
 * Provides the defineCodepurifyConfig helper function for users to define
 * their Codepurify configuration with type safety and validation.
 */

import { CodepurifyConfig } from '../types/codepurify.config.types';

/**
 * Helper function to define Codepurify configuration
 *
 * This function provides type safety and validation for user-defined
 * Codepurify configuration. It can be used in config files like:
 *
 * ```js
 * const { defineCodepurifyConfig } = require("codepurify");
 *
 * module.exports = defineCodepurifyConfig({
 *   project: {
 *     name: "my-app"
 *   }
 * });
 * ```
 *
 * @param config - User configuration object
 * @returns Enhanced configuration object with template filtering methods
 */
export function defineCodepurifyConfig(config: CodepurifyConfig): CodepurifyConfig {
  // Basic validation to ensure config is an object
  if (typeof config !== 'object' || config === null) {
    throw new Error('Codepurify config must be an object');
  }

  return config;
}
