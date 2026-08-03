import { readFile } from "node:fs/promises";
import { dirname, relative, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";
import matter from "gray-matter";

const scriptDirectory = dirname(fileURLToPath(import.meta.url));
const workspaceRoot = resolve(scriptDirectory, "../../..");
const docsRoot = resolve(workspaceRoot, ".docs/public");
const warnings = [];
const publicPaths = new Set();
const sources = new Set();
const documents = new Map();

function warn(message) {
  warnings.push(message);
  console.warn(`[docs] ${message}`);
}

function isValidPath(value, { allowRoot = false } = {}) {
  if (allowRoot && value === "") return true;
  return (
    typeof value === "string" &&
    /^[a-z0-9][a-z0-9/_-]*$/.test(value) &&
    !value.includes("..") &&
    !value.endsWith("/") &&
    !value.includes("//")
  );
}

function resolveDocumentSource(item) {
  const source = typeof item.source === "string" ? item.source : item.path;
  if (!isValidPath(source)) {
    return { error: `Invalid documentation source: ${String(source)}` };
  }

  const sourceFile = resolve(docsRoot, `${source}.md`);
  const relativePath = relative(docsRoot, sourceFile);
  if (!relativePath || relativePath.startsWith("..") || relativePath.split(sep).includes("..")) {
    return { error: `Documentation source escapes .docs/public/: ${source}` };
  }
  return { source, sourceFile };
}

let navigation;
try {
  navigation = JSON.parse(await readFile(resolve(docsRoot, "navigation.json"), "utf8"));
} catch (error) {
  warn(`Unable to read navigation.json: ${error instanceof Error ? error.message : String(error)}`);
  navigation = { sections: [], redirects: {} };
}

let ecosystem;
try {
  ecosystem = JSON.parse(await readFile(resolve(docsRoot, "ecosystem.json"), "utf8"));
} catch (error) {
  warn(`Unable to read ecosystem.json: ${error instanceof Error ? error.message : String(error)}`);
  ecosystem = { products: [], stages: [] };
}

async function validateItem(item, { parentPath = null, inheritedPackage = null } = {}) {
  const path = item?.path;
  if (!isValidPath(path, { allowRoot: parentPath === null })) {
    warn(`Invalid documentation path: ${String(path)}`);
    return;
  }
  if (parentPath !== null && !path.startsWith(`${parentPath}/`)) {
    warn(`Documentation child ${path} is not nested under ${parentPath}.`);
  }
  if (publicPaths.has(path)) {
    warn(`Duplicate documentation path: ${path || "(root)"}`);
    return;
  }
  publicPaths.add(path);

  const resolved = resolveDocumentSource(item);
  if (resolved.error) {
    warn(resolved.error);
    return;
  }
  if (sources.has(resolved.source)) {
    warn(`Documentation source ${resolved.source}.md is published more than once.`);
  }
  sources.add(resolved.source);

  try {
    const content = await readFile(resolved.sourceFile, "utf8");
    const normalized = content.replace(/^\uFEFF/, "").replace(/\r\n/g, "\n");
    if (!normalized.startsWith("---\n")) {
      warn(`Documentation source ${resolved.source}.md has no YAML frontmatter.`);
    }
    const parsed = matter(normalized);
    if (typeof parsed.data.title !== "string" || !parsed.data.title.trim()) {
      warn(`Documentation source ${resolved.source}.md has no frontmatter title.`);
    }
    if (
      parsed.data.description !== undefined &&
      (typeof parsed.data.description !== "string" || !parsed.data.description.trim())
    ) {
      warn(`Documentation source ${resolved.source}.md has an invalid frontmatter description.`);
    }

    const packageId =
      typeof item.package === "string"
        ? item.package
        : inheritedPackage ?? (typeof parsed.data.product === "string" ? parsed.data.product : null);
    if (packageId && parsed.data.product && parsed.data.product !== packageId) {
      warn(
        `Documentation ${resolved.source}.md declares product ${String(parsed.data.product)} but navigation assigns ${packageId}.`,
      );
    }

    documents.set(path, {
      content: normalized,
      source: resolved.source,
      product: packageId ?? parsed.data.product,
    });

    for (const child of item.children ?? []) {
      await validateItem(child, { parentPath: path, inheritedPackage: packageId });
    }
  } catch (error) {
    warn(`Unable to read ${resolved.source}.md: ${error instanceof Error ? error.message : String(error)}`);
  }
}

if (!navigation.home) {
  warn("navigation.json has no home document.");
} else {
  await validateItem(navigation.home, { parentPath: null });
}

for (const section of navigation.sections ?? []) {
  if (typeof section.title !== "string" || !section.title.trim()) {
    warn("A public documentation section has no title.");
  }
  for (const item of section.items ?? []) {
    await validateItem(item, { parentPath: null });
  }
}

const redirects = navigation.redirects ?? {};
for (const [sourcePath, targetPath] of Object.entries(redirects)) {
  if (!isValidPath(sourcePath) || !isValidPath(targetPath)) {
    warn(`Invalid documentation redirect: ${sourcePath} -> ${String(targetPath)}.`);
    continue;
  }
  if (publicPaths.has(sourcePath)) {
    warn(`Documentation redirect source ${sourcePath} conflicts with a published page.`);
  }
  if (!publicPaths.has(targetPath)) {
    warn(`Documentation redirect ${sourcePath} points to unpublished ${targetPath}.`);
  }
}

const linkPattern = /\]\(\/docs(?:\/([a-z0-9][a-z0-9/_-]*))?(?:#[^)]+)?\)/g;
for (const [, document] of documents) {
  for (const match of document.content.matchAll(linkPattern)) {
    const target = match[1] ?? "";
    const redirectedTarget = redirects[target];
    if (!publicPaths.has(target) && !(redirectedTarget && publicPaths.has(redirectedTarget))) {
      warn(`Documentation ${document.source}.md links to unpublished /docs${target ? `/${target}` : ""}.`);
    }
  }
}

const productIds = new Set();
for (const product of ecosystem.products ?? []) {
  if (typeof product.id !== "string" || !/^[a-z0-9-]+$/.test(product.id)) {
    warn(`Invalid ecosystem product id: ${String(product.id)}`);
    continue;
  }
  if (productIds.has(product.id)) {
    warn(`Duplicate ecosystem product id: ${product.id}`);
  }
  productIds.add(product.id);

  const docsPath = product.docsSlug;
  const redirectedDocsPath = typeof docsPath === "string" ? redirects[docsPath] : undefined;
  if (
    typeof docsPath !== "string" ||
    (!publicPaths.has(docsPath) && !(redirectedDocsPath && publicPaths.has(redirectedDocsPath)))
  ) {
    warn(`Ecosystem product ${product.id} points to unpublished docs path ${String(docsPath)}.`);
  }

  for (const link of product.links ?? []) {
    if (!link || typeof link.label !== "string" || !link.label.trim()) {
      warn(`Ecosystem product ${product.id} has an invalid external link label.`);
    }
    if (link.status === "available" && (typeof link.url !== "string" || !/^https:\/\//.test(link.url))) {
      warn(`Available link ${String(link.label)} for ${product.id} has no valid HTTPS URL.`);
    }
    if (link.status === "tbd" && link.url !== null) {
      warn(`TBD link ${String(link.label)} for ${product.id} must use a null URL.`);
    }
  }
}

for (const [path, document] of documents) {
  if (typeof document.product === "string" && !productIds.has(document.product)) {
    warn(`Documentation ${path || "(root)"} references unknown ecosystem product ${document.product}.`);
  }
}

for (const stage of ecosystem.stages ?? []) {
  for (const productId of stage.products ?? []) {
    if (!productIds.has(productId)) {
      warn(`Ecosystem stage ${String(stage.id)} references unknown product ${String(productId)}.`);
    }
  }
}

if (warnings.length === 0) {
  console.log(
    `Validated ${publicPaths.size} nested Markdown documentation pages, ${Object.keys(redirects).length} redirects, and ${productIds.size} ecosystem products.`,
  );
} else {
  console.warn(`[docs] Validation completed with ${warnings.length} warning${warnings.length === 1 ? "" : "s"}.`);
  process.exitCode = 1;
}
