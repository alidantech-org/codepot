import { cp, mkdir, rm, stat } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDirectory = dirname(fileURLToPath(import.meta.url));
const appRoot = resolve(scriptDirectory, "..");
const standaloneAppRoot = resolve(appRoot, ".next/standalone/apps/site");
const standaloneServer = resolve(standaloneAppRoot, "server.js");

async function requirePath(path, label) {
  try {
    await stat(path);
  } catch {
    throw new Error(`${label} was not produced: ${path}`);
  }
}

async function replaceDirectory(source, target) {
  await requirePath(source, "Required standalone asset directory");
  await rm(target, { recursive: true, force: true });
  await mkdir(dirname(target), { recursive: true });
  await cp(source, target, { recursive: true });
}

await requirePath(standaloneServer, "Standalone Next.js server");
await replaceDirectory(
  resolve(appRoot, ".next/static"),
  resolve(standaloneAppRoot, ".next/static"),
);
await replaceDirectory(
  resolve(appRoot, "public"),
  resolve(standaloneAppRoot, "public"),
);

console.log(`Prepared standalone site at ${standaloneAppRoot}`);
