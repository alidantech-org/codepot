/**
 * codepot Template Path Helpers
 *
 * Path tokens and file name builder for template output paths.
 */

/**
 * codepot template path token helpers.
 *
 * These are strongly typed placeholder tokens that can be used to build
 * output paths without manually writing codepot path strings everywhere.
 */
export const paths = {
  entity: {
    key: '{{entity.key}}',
    groupKey: '{{entity.group_key}}',

    name: {
      pascal: '{{entity.name.pascal}}',
      camel: '{{entity.name.camel}}',
      kebab: '{{entity.name.kebab}}',
      snake: '{{entity.name.snake}}',
    },
  },

  template: {
    name: '{{template.name}}',
  },
} as const;

export type codepotPathToken =
  | typeof paths.entity.key
  | typeof paths.entity.groupKey
  | typeof paths.entity.name.pascal
  | typeof paths.entity.name.camel
  | typeof paths.entity.name.kebab
  | typeof paths.entity.name.snake
  | typeof paths.template.name;

export type codepotOutputFolderPart = string | codepotPathToken;

export type codepotOutputFolder = readonly codepotOutputFolderPart[];

/**
 * File name builder result type.
 */
export interface codepotOutputFileName {
  /**
   * Base token for the filename.
   */
  base: codepotPathToken;

  /**
   * Optional prefix to add before the base token.
   */
  prefix?: string;

  /**
   * Optional suffix to add after the base token.
   */
  suffix?: string;

  /**
   * File extension (without dot).
   */
  ext: string;
}

/**
 * File name builder API.
 */
export function file(base: codepotPathToken) {
  return {
    prefix: (prefix: string) => ({
      suffix: (suffix: string) => ({
        ext: (ext: string) =>
          ({
            base,
            prefix,
            suffix,
            ext,
          }) as codepotOutputFileName,
      }),
      ext: (ext: string) =>
        ({
          base,
          prefix,
          ext,
        }) as codepotOutputFileName,
    }),
    suffix: (suffix: string) => ({
      ext: (ext: string) =>
        ({
          base,
          suffix,
          ext,
        }) as codepotOutputFileName,
    }),
    ext: (ext: string) =>
      ({
        base,
        ext,
      }) as codepotOutputFileName,
  };
}
