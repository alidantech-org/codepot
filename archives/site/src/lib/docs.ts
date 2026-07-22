import fs from "node:fs/promises";
import path from "node:path";
import matter from "gray-matter";
import GithubSlugger from "github-slugger";

export interface DocFrontmatter {
  title?: string;
  description?: string;
  order?: number;
  published?: boolean;
  lastModified?: string;
  group?: string;
  [key: string]: unknown;
}

export interface Heading {
  id: string;
  text: string;
  level: number;
}

export interface Doc {
  slug: string;
  title: string;
  description?: string;
  content: string;
  frontmatter: DocFrontmatter;
  headings: Heading[];
  filePath: string;
  prev?: Pick<Doc, "slug" | "title" | "description">;
  next?: Pick<Doc, "slug" | "title" | "description">;
}

export interface DocItem {
  slug: string;
  title: string;
  description?: string;
  group?: string;
  children?: DocItem[];
}

export interface DocNavigation {
  title: string;
  items: DocNavItem[];
}

export interface DocNavItem {
  title: string;
  href: string;
  isActive?: boolean;
  children?: DocNavItem[];
}

interface RegistryEntry {
  slug: string;
  realSlug: string;
  filePath: string;
}

interface DocsRegistry {
  entries: RegistryEntry[];
  slugToEntry: Map<string, RegistryEntry>;
}

const docsDirectory = path.resolve(process.cwd(), "..", "docs");

let registryCache: Promise<DocsRegistry> | null = null;
let docsCache: Promise<Doc[]> | null = null;

function normalizeSlug(slug: string): string {
  return slug
    .replace(/\\/g, "/")
    .replace(/^\//, "")
    .replace(/\.md$/, "")
    .replace(/\/index$/, "");
}

function cleanRouteSegment(segment: string): string {
  return segment.replace(/^(\d+)-/, "");
}

function toPublicSlug(realSlug: string): string {
  return normalizeSlug(realSlug).split("/").map(cleanRouteSegment).join("/");
}

function getFolderOrder(folder?: string): number {
  if (!folder) return Number.POSITIVE_INFINITY;

  const match = folder.match(/^(\d+)-/);
  return match ? Number(match[1]) : Number.POSITIVE_INFINITY;
}

function cleanFolderName(folder?: string): string {
  if (!folder) return "";

  return folder
    .replace(/^(\d+)-/, "")
    .replace(/-/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function toTitleCase(value: string): string {
  return value
    .replace(/^(\d+)-/, "")
    .replace(/[-_]+/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

async function pathExists(targetPath: string): Promise<boolean> {
  try {
    await fs.access(targetPath);
    return true;
  } catch {
    return false;
  }
}

async function getAllMarkdownFiles(
  dir: string,
  basePath = "",
): Promise<string[]> {
  if (!(await pathExists(dir))) return [];

  const entries = await fs.readdir(dir, { withFileTypes: true });

  const sortedEntries = entries.sort((a, b) => {
    if (a.isFile() && b.isDirectory()) return -1;
    if (a.isDirectory() && b.isFile()) return 1;
    return a.name.localeCompare(b.name);
  });

  const files: string[] = [];

  for (const entry of sortedEntries) {
    if (entry.name.startsWith(".")) continue;

    const fullPath = path.join(dir, entry.name);
    const relativePath = path.join(basePath, entry.name);

    if (entry.isDirectory()) {
      const nested = await getAllMarkdownFiles(fullPath, relativePath);
      files.push(...nested);
      continue;
    }

    if (entry.isFile() && entry.name.endsWith(".md")) {
      files.push(normalizeSlug(relativePath));
    }
  }

  return files;
}

async function buildRegistry(): Promise<DocsRegistry> {
  const realSlugs = await getAllMarkdownFiles(docsDirectory);
  const entries: RegistryEntry[] = realSlugs.map((realSlug) => {
    const normalizedRealSlug = normalizeSlug(realSlug);

    return {
      slug: toPublicSlug(normalizedRealSlug),
      realSlug: normalizedRealSlug,
      filePath: path.join(docsDirectory, `${normalizedRealSlug}.md`),
    };
  });

  const slugToEntry = new Map<string, RegistryEntry>();

  for (const entry of entries) {
    slugToEntry.set(entry.slug, entry);
  }

  return {
    entries,
    slugToEntry,
  };
}

async function getRegistry(): Promise<DocsRegistry> {
  registryCache ??= buildRegistry();
  return registryCache;
}

function extractHeadings(content: string): Heading[] {
  const headings: Heading[] = [];
  const slugger = new GithubSlugger();

  for (const line of content.split("\n")) {
    const match = line.match(/^(#{1,6})\s+(.+)$/);
    if (!match) continue;

    const level = match[1].length;
    const rawText = match[2].replace(/#+$/, "").trim();
    if (!rawText) continue;

    const text = rawText
      .replace(/`([^`]+)`/g, "$1")
      .replace(/\*\*([^*]+)\*\*/g, "$1")
      .replace(/\*([^*]+)\*/g, "$1")
      .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
      .trim();

    headings.push({
      id: slugger.slug(text),
      text,
      level,
    });
  }

  return headings;
}

function getDocTitle(slug: string, frontmatter: DocFrontmatter): string {
  if (typeof frontmatter.title === "string" && frontmatter.title.trim()) {
    return frontmatter.title.trim();
  }

  const lastPart = slug.split("/").filter(Boolean).pop();
  return lastPart ? toTitleCase(lastPart) : "Untitled";
}

function isPublished(frontmatter: DocFrontmatter): boolean {
  return frontmatter.published !== false;
}

function toDocSummary(doc: Doc): Pick<Doc, "slug" | "title" | "description"> {
  return {
    slug: doc.slug,
    title: doc.title,
    description: doc.description,
  };
}

async function loadDocFromEntry(entry: RegistryEntry): Promise<Doc | null> {
  try {
    const fileContents = await fs.readFile(entry.filePath, "utf8");
    const parsed = matter(fileContents);

    const frontmatter = parsed.data as DocFrontmatter;

    if (!isPublished(frontmatter)) {
      return null;
    }

    const content = parsed.content.trim();

    return {
      slug: entry.slug,
      title: getDocTitle(entry.slug, frontmatter),
      description:
        typeof frontmatter.description === "string"
          ? frontmatter.description
          : undefined,
      content,
      frontmatter,
      headings: extractHeadings(content),
      filePath: entry.filePath,
    };
  } catch (error) {
    console.error(`Failed to load doc "${entry.slug}":`, error);
    return null;
  }
}

function sortDocs(docs: Doc[]): Doc[] {
  return [...docs].sort((a, b) => {
    const aSection = a.filePath
      .replace(docsDirectory, "")
      .split(path.sep)
      .filter(Boolean)[0];

    const bSection = b.filePath
      .replace(docsDirectory, "")
      .split(path.sep)
      .filter(Boolean)[0];

    const sectionOrderA = getFolderOrder(aSection);
    const sectionOrderB = getFolderOrder(bSection);

    if (sectionOrderA !== sectionOrderB) {
      return sectionOrderA - sectionOrderB;
    }

    const orderA = a.frontmatter.order ?? Number.POSITIVE_INFINITY;
    const orderB = b.frontmatter.order ?? Number.POSITIVE_INFINITY;

    if (orderA !== orderB) {
      return orderA - orderB;
    }

    return a.title.localeCompare(b.title);
  });
}

async function loadAllDocs(): Promise<Doc[]> {
  docsCache ??= (async () => {
    const registry = await getRegistry();
    const docs = await Promise.all(registry.entries.map(loadDocFromEntry));

    return sortDocs(docs.filter((doc): doc is Doc => doc !== null));
  })();

  return docsCache;
}

function getNavigationDocs(
  currentSlug: string,
  allDocs: Doc[],
): {
  prev?: Pick<Doc, "slug" | "title" | "description">;
  next?: Pick<Doc, "slug" | "title" | "description">;
} {
  const normalizedSlug = normalizeSlug(currentSlug);
  const index = allDocs.findIndex((doc) => doc.slug === normalizedSlug);

  if (index === -1) return {};

  return {
    prev: index > 0 ? toDocSummary(allDocs[index - 1]) : undefined,
    next:
      index < allDocs.length - 1 ? toDocSummary(allDocs[index + 1]) : undefined,
  };
}

function generateNavigation(docs: Doc[]): DocNavigation[] {
  const sections = new Map<string, Doc[]>();

  for (const doc of docs) {
    const [section = "docs"] = doc.slug.split("/");
    const sectionKey = doc.frontmatter.group || section;

    const existing = sections.get(sectionKey) ?? [];
    existing.push(doc);
    sections.set(sectionKey, existing);
  }

  return Array.from(sections.entries())
    .sort(([a], [b]) => {
      const orderA = getFolderOrder(a);
      const orderB = getFolderOrder(b);

      if (orderA !== orderB) return orderA - orderB;
      return a.localeCompare(b);
    })
    .map(([section, sectionDocs]) => ({
      title: cleanFolderName(section),
      items: sortDocs(sectionDocs).map((doc) => ({
        title: doc.title,
        href: `/docs/${doc.slug}`,
      })),
    }));
}

export async function generateStaticParams(): Promise<{ doc: string[] }[]> {
  const docs = await loadAllDocs();

  return docs.map((doc) => ({
    doc: doc.slug.split("/").filter(Boolean),
  }));
}

export async function getDocBySlug(slug: string): Promise<Doc | null> {
  const normalizedSlug = normalizeSlug(slug);
  const allDocs = await loadAllDocs();
  const doc = allDocs.find((item) => item.slug === normalizedSlug);

  if (!doc) return null;

  const { prev, next } = getNavigationDocs(normalizedSlug, allDocs);

  return {
    ...doc,
    prev,
    next,
  };
}

export async function getAllDocsForNavigation(): Promise<DocNavigation[]> {
  const docs = await loadAllDocs();
  return generateNavigation(docs);
}

export function generateDocMetadata(doc: Doc): {
  title: string;
  description: string;
} {
  return {
    title: `${doc.title} - CodePurify Documentation`,
    description: doc.description ?? `Documentation for ${doc.title}`,
  };
}

export async function searchDocs(query: string): Promise<Doc[]> {
  const trimmedQuery = query.trim().toLowerCase();

  if (!trimmedQuery) return [];

  const allDocs = await loadAllDocs();

  return allDocs.filter((doc) => {
    const searchableText = [doc.title, doc.description, doc.content, doc.slug]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();

    return searchableText.includes(trimmedQuery);
  });
}

export async function getAllDocs(): Promise<DocItem[]> {
  const allDocs = await loadAllDocs();

  return allDocs.map((doc) => {
    const [section] = doc.slug.split("/");

    return {
      slug: doc.slug,
      title: doc.title,
      description: doc.description,
      group: section ? cleanFolderName(section) : undefined,
    };
  });
}
