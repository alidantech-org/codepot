import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, relative, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";
import GithubSlugger from "github-slugger";
import matter from "gray-matter";

const scriptDirectory = dirname(fileURLToPath(import.meta.url));
const appRoot = resolve(scriptDirectory, "..");
const workspaceRoot = resolve(appRoot, "../..");
const docsRoot = resolve(workspaceRoot, "docs");
const generatedRoot = resolve(appRoot, "src/generated");
const docsOutput = resolve(generatedRoot, "docs.ts");
const tocOutput = resolve(generatedRoot, "docs-toc.json");

const navigation = JSON.parse(await readFile(resolve(docsRoot, "navigation.json"), "utf8"));
const ecosystem = JSON.parse(await readFile(resolve(docsRoot, "ecosystem.json"), "utf8"));
const documents = {};
const tablesOfContents = {};
const index = [];
const searchIndex = [];
const seen = new Set();

function resolveDocumentSource(item) {
  const source = typeof item.source === "string" ? item.source : item.slug;
  if (!/^[a-z0-9][a-z0-9/_-]*$/.test(source) || source.includes("..") || source.endsWith("/")) {
    throw new Error(`Invalid documentation source: ${String(source)}`);
  }

  const sourceFile = resolve(docsRoot, `${source}.md`);
  const relativePath = relative(docsRoot, sourceFile);
  if (!relativePath || relativePath.startsWith("..") || relativePath.split(sep).includes("..")) {
    throw new Error(`Documentation source escapes docs/: ${source}`);
  }
  return { source, sourceFile };
}

function cleanHeadingText(value) {
  return value
    .replace(/\s+#+\s*$/, "")
    .replace(/`([^`]+)`/g, "$1")
    .replace(/!\[([^\]]*)\]\([^)]+\)/g, "$1")
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    .replace(/<[^>]+>/g, "")
    .replace(/\*\*([^*]+)\*\*/g, "$1")
    .replace(/__([^_]+)__/g, "$1")
    .replace(/\*([^*]+)\*/g, "$1")
    .replace(/_([^_]+)_/g, "$1")
    .replace(/\\([#*_`])/g, "$1")
    .trim();
}

function cleanMarkdownText(value) {
  return value
    .replace(/```[\s\S]*?```/g, " ")
    .replace(/~~~[\s\S]*?~~~/g, " ")
    .replace(/!\[([^\]]*)\]\([^)]+\)/g, "$1")
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    .replace(/<[^>]+>/g, " ")
    .replace(/[`*_>#|]/g, " ")
    .replace(/^[-+]\s+/gm, " ")
    .replace(/^\d+\.\s+/gm, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function normalizeSearchText(value) {
  return value
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9+#./_-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function createSnippet(value, maximumLength = 190) {
  const clean = cleanMarkdownText(value);
  if (clean.length <= maximumLength) return clean;
  const shortened = clean.slice(0, maximumLength + 1);
  const boundary = shortened.lastIndexOf(" ");
  return `${shortened.slice(0, boundary > 120 ? boundary : maximumLength).trim()}…`;
}

function extractDocumentData(content) {
  const headings = [];
  const sections = [];
  const slugger = new GithubSlugger();
  let fence = null;
  let current = null;

  for (const line of content.split(/\r?\n/)) {
    const fenceMatch = line.match(/^\s*(```+|~~~+)/);
    if (fenceMatch) {
      const marker = fenceMatch[1][0];
      fence = fence === marker ? null : fence ?? marker;
      continue;
    }
    if (fence) continue;

    const match = line.match(/^\s{0,3}(#{1,6})\s+(.+?)\s*$/);
    if (match) {
      const text = cleanHeadingText(match[2]);
      if (!text) continue;

      const heading = {
        id: slugger.slug(text),
        text,
        level: match[1].length,
      };
      headings.push(heading);

      if (heading.level >= 2 && heading.level <= 3) {
        current = { ...heading, lines: [] };
        sections.push(current);
      } else if (heading.level <= 2) {
        current = null;
      }
      continue;
    }

    if (current && line.trim()) current.lines.push(line.trim());
  }

  return { headings, sections };
}

for (const section of navigation.sections ?? []) {
  for (const item of section.items ?? []) {
    const slug = item.slug;
    if (typeof slug !== "string" || !/^[a-z0-9-]+$/.test(slug)) {
      throw new Error(`Invalid public documentation slug: ${String(slug)}`);
    }
    if (seen.has(slug)) {
      throw new Error(`Duplicate public documentation slug: ${slug}`);
    }
    seen.add(slug);

    const { source, sourceFile } = resolveDocumentSource(item);
    const markdown = await readFile(sourceFile, "utf8");
    const parsed = matter(markdown);
    const title = String(parsed.data.title ?? item.title ?? slug);
    const description = String(parsed.data.description ?? "");
    const sectionTitle = String(section.title ?? "Documentation");
    const { headings, sections } = extractDocumentData(parsed.content);
    const pageSnippet = description || createSnippet(parsed.content);

    documents[slug] = markdown;
    tablesOfContents[slug] = headings;
    index.push({
      slug,
      source,
      title,
      description,
      section: sectionTitle,
      product: typeof parsed.data.product === "string" ? parsed.data.product : null,
      searchText: normalizeSearchText(`${title} ${description} ${parsed.content}`),
    });

    searchIndex.push({
      id: `page:${slug}`,
      kind: "page",
      slug,
      href: `/docs/${slug}`,
      title,
      pageTitle: title,
      section: sectionTitle,
      description,
      snippet: pageSnippet,
      level: 1,
      searchText: normalizeSearchText(`${title} ${description} ${sectionTitle} ${parsed.content}`),
    });

    for (const heading of sections) {
      const body = heading.lines.join(" ");
      searchIndex.push({
        id: `heading:${slug}:${heading.id}`,
        kind: "heading",
        slug,
        href: `/docs/${slug}#${heading.id}`,
        title: heading.text,
        pageTitle: title,
        section: sectionTitle,
        description,
        snippet: createSnippet(body || description || parsed.content),
        level: heading.level,
        searchText: normalizeSearchText(`${heading.text} ${title} ${description} ${sectionTitle} ${body}`),
      });
    }
  }
}

const source = [
  "// Generated by scripts/sync-docs.mjs. Do not edit.",
  `export const DOCS = ${JSON.stringify(documents, null, 2)} as const;`,
  `export const NAVIGATION = ${JSON.stringify(navigation, null, 2)} as const;`,
  `export const DOC_INDEX = ${JSON.stringify(index, null, 2)} as const;`,
  `export const DOC_SEARCH_INDEX = ${JSON.stringify(searchIndex, null, 2)} as const;`,
  `export const ECOSYSTEM = ${JSON.stringify(ecosystem, null, 2)} as const;`,
  "export type DocSlug = keyof typeof DOCS;",
  "",
].join("\n");

await mkdir(generatedRoot, { recursive: true });
await Promise.all([
  writeFile(docsOutput, source, "utf8"),
  writeFile(tocOutput, `${JSON.stringify(tablesOfContents, null, 2)}\n`, "utf8"),
]);
console.log(
  `Synced ${Object.keys(documents).length} public documentation files, ${searchIndex.length} search records, JSON tables of contents, and ecosystem metadata.`,
);
