import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDirectory = dirname(fileURLToPath(import.meta.url));
const workspaceRoot = resolve(scriptDirectory, "../../..");
const docsRoot = resolve(workspaceRoot, "docs");
const navigation = JSON.parse(await readFile(resolve(docsRoot, "navigation.json"), "utf8"));
const slugs = new Set();
const documents = new Map();

for (const section of navigation.sections ?? []) {
  if (typeof section.title !== "string" || !section.title.trim()) {
    throw new Error("Every public documentation section requires a title.");
  }
  for (const item of section.items ?? []) {
    if (typeof item.slug !== "string" || !/^[a-z0-9-]+$/.test(item.slug)) {
      throw new Error(`Invalid documentation slug: ${String(item.slug)}`);
    }
    if (slugs.has(item.slug)) {
      throw new Error(`Duplicate documentation slug: ${item.slug}`);
    }
    slugs.add(item.slug);
    const content = await readFile(resolve(docsRoot, `${item.slug}.md`), "utf8");
    if (!content.startsWith("---\n")) {
      throw new Error(`Documentation file ${item.slug}.md requires frontmatter.`);
    }
    documents.set(item.slug, content);
  }
}

const linkPattern = /\]\(\/docs\/([a-z0-9-]+)(?:#[^)]+)?\)/g;
for (const [slug, content] of documents) {
  for (const match of content.matchAll(linkPattern)) {
    const target = match[1];
    if (!slugs.has(target)) {
      throw new Error(`Documentation ${slug}.md links to unpublished /docs/${target}.`);
    }
  }
}

console.log(`Validated ${slugs.size} public Markdown documentation pages.`);
