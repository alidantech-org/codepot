import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDirectory = dirname(fileURLToPath(import.meta.url));
const workspaceRoot = resolve(scriptDirectory, "../../..");
const docsRoot = resolve(workspaceRoot, "docs");
const warnings = [];
const slugs = new Set();
const documents = new Map();

/**
 * Documentation validation is advisory during local development. It reports
 * content problems without blocking the site, while sync-docs remains the
 * authoritative build step for files that are genuinely required.
 */
function warn(message) {
  warnings.push(message);
  console.warn(`[docs] ${message}`);
}

let navigation;
try {
  navigation = JSON.parse(await readFile(resolve(docsRoot, "navigation.json"), "utf8"));
} catch (error) {
  warn(`Unable to read navigation.json: ${error instanceof Error ? error.message : String(error)}`);
  navigation = { sections: [] };
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

    try {
      const content = await readFile(resolve(docsRoot, `${item.slug}.md`), "utf8");
      const normalized = content.replace(/^\uFEFF/, "").replace(/\r\n/g, "\n");
      if (!normalized.startsWith("---\n")) {
        warn(`Documentation file ${item.slug}.md has no YAML frontmatter.`);
      }
      documents.set(item.slug, normalized);
    } catch (error) {
      warn(`Unable to read ${item.slug}.md: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
}

const linkPattern = /\]\(\/docs\/([a-z0-9-]+)(?:#[^)]+)?\)/g;
for (const [slug, content] of documents) {
  for (const match of content.matchAll(linkPattern)) {
    const target = match[1];
    if (target && !slugs.has(target)) {
      warn(`Documentation ${slug}.md links to unpublished /docs/${target}.`);
    }
  }
}

if (warnings.length === 0) {
  console.log(`Validated ${slugs.size} public Markdown documentation pages.`);
} else {
  console.warn(`[docs] Validation completed with ${warnings.length} warning${warnings.length === 1 ? "" : "s"}.`);
}
