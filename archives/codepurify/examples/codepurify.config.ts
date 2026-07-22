import { defineCodepurifyConfig } from 'codepurify';

export default defineCodepurifyConfig({
  rootDir: process.cwd(),
  outputDir: './src/generated',
  manifestPath: './codepurify/manifest.json',

  // Config directories with dynamic inference
  entitiesDir: '__CODEPURIFY_ENTITIES_DIR__',
  resourcesDir: '__CODEPURIFY_RESOURCES_DIR__',
});
