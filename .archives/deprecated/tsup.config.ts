import { defineConfig } from 'tsup';

export default defineConfig({
  entry: {
    index: 'src/index.ts',
    'cli/index': 'cli/index.ts',
  },
  format: ['esm', 'cjs'], // 👈 Compiles both .js (ESM) and .cjs (CommonJS)
  dts: true, // 👈 Generates .d.ts files for both formats
  shims: true, // 👈 Adds missing CJS/ESM compatibility shims
  sourcemap: true,
  clean: true,
  splitting: false,
  bundle: true,
  target: 'node18',
  platform: 'node',
});
