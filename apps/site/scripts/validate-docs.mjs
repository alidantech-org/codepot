import { readFile } from "node:fs/promises";
import { dirname, relative, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";
import matter from "gray-matter";

const scriptDirectory = dirname(fileURLToPath(import.meta.url));
const workspaceRoot = resolve(scriptDirectory, "../../..");
const docsRoot = resolve(workspaceRoot, "docs");
const warnings = [];
const slugs = new Set();
const documents = new Map();

function warn(message) {
  warnings.push(message);
  console.warn(`[docs] ${message}`);
}

function resolveDocumentSource(item) {
  const source = typeof item.source === "string" ? item.source : item.slug;
  if (typeof source !== "string" || !/^[a-z0-9][a-z0-9/_-]*$/.test(source) || source.includes("..") || source.endsWith("/")) {
    return { error: `Invalid documentation source: ${String(source)}` };
  }

  const sourceFile = resolve(docsRoot, `${source}.md`);
  const relativePath = relative(docsRoot, sourceFile);
  if (!relativePath || relativePath.startsWith("..") || relativePath.split(sep).includes("..")) {
    return { error: `Documentation source escapes docs/: ${source}` };
  }
  return { source, sourceFile };
}

let navigation;
try {
  navigation = JSON.parse(await readFile(resolve(docsRoot, "navigation.json"), "utf8"));
} catch (error) {
  warn(`Unable to read navigation.json: ${error instanceof Error ? error.message : String(error)}`);
  navigation = { sections: [] };
}

let ecosystem;
try {
  ecosystem = JSON.parse(await readFile(resolve(docsRoot, "ecosystem.json"), "utf8"));
} catch (error) {
  warn(`Unable to read ecosystem.json: ${error instanceof Error ? error.message : String(error)}`);
  ecosystem = { products: [], stages: [] };
}

for (const section of navigation.sections ?? []) {
  if (typeof section.title !== "string" || !section.title.trim()) {
    warn("A public documentation section has no title.");
  }

  for (const item of section.items ?? []) {
    if (typeof item.slug !== "string" || !/^[a-z0-9-]+$/.test(item.slug)) {
      warn(`Invalid documentation slug: ${String(item.slug)}`);
      continue;
    }

    if (slugs.has(item.slug)) {
      warn(`Duplicate documentation slug: ${item.slug}`);
      continue;
    }
    slugs.add(item.slug);

    const resolved = resolveDocumentSource(item);
    if (resolved.error) {
      warn(resolved.error);
      continue;
    }

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
      documents.set(item.slug, { content: normalized, source: resolved.source, product: parsed.data.product });
    } catch (error) {
      warn(`Unable to read ${resolved.source}.md: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
}

const linkPattern = /\]\(\/docs\/([a-z0-9-]+)(?:#[^)]+)?\)/g;
for (const [slug, document] of documents) {
  for (const match of document.content.matchAll(linkPattern)) {
    const target = match[1];
    if (target && !slugs.has(target)) {
      warn(`Documentation ${document.source}.md links to unpublished /docs/${target}.`);
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

  if (typeof product.docsSlug !== "string" || !slugs.has(product.docsSlug)) {
    warn(`Ecosystem product ${product.id} points to unpublished docs slug ${String(product.docsSlug)}.`);
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

for (const [slug, document] of documents) {
  if (typeof document.product === "string" && !productIds.has(document.product)) {
    warn(`Documentation ${slug} references unknown ecosystem product ${document.product}.`);
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
  console.log(`Validated ${slugs.size} public Markdown documentation pages and ${productIds.size} ecosystem products.`);
} else {
  console.warn(`[docs] Validation completed with ${warnings.length} warning${warnings.length === 1 ? "" : "s"}.`);
  process.exitCode = 1;
}
