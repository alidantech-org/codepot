import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { build } from 'esbuild';

const CONFIG_FILE_NAMES = ['package.config.ts', 'package.config.mts', 'package.config.js', 'package.config.mjs'];

export async function loadPackageConfig(cwd = process.cwd()) {
  const configPath = await findPackageConfig(cwd);
  const bundledPath = await bundlePackageConfig(configPath, cwd);

  const module = await import(pathToFileURL(bundledPath).href);
  const config = module.default ?? module.config;

  if (!config) {
    throw new Error('Package config must export a default config or named `config` export.');
  }

  return config;
}

async function findPackageConfig(cwd: string): Promise<string> {
  for (const fileName of CONFIG_FILE_NAMES) {
    const fullPath = path.resolve(cwd, fileName);

    try {
      await fs.access(fullPath);
      return fullPath;
    } catch {
      // keep looking
    }
  }

  throw new Error(`No package config found. Expected one of: ${CONFIG_FILE_NAMES.join(', ')}`);
}

async function bundlePackageConfig(configPath: string, cwd: string): Promise<string> {
  const cacheDir = path.resolve(cwd, 'node_modules/.cache/codepot-openapi');
  const outfile = path.join(cacheDir, 'package.config.mjs');

  await fs.mkdir(cacheDir, { recursive: true });

  await build({
    entryPoints: [configPath],
    outfile,
    bundle: true,
    platform: 'node',
    target: 'node20',
    format: 'esm',
    sourcemap: 'inline',
    absWorkingDir: cwd,
    tsconfig: await resolveTsConfig(cwd),
    packages: 'external',
    external: ['codepot-openapi', 'zod'],
  });

  return outfile;
}

async function resolveTsConfig(cwd: string): Promise<string | undefined> {
  const tsconfigPath = path.resolve(cwd, 'tsconfig.json');

  try {
    await fs.access(tsconfigPath);
    return tsconfigPath;
  } catch {
    return undefined;
  }
}
