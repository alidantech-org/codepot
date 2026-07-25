import type { Metadata } from "next";
import matter from "gray-matter";

import tocData from "@/generated/docs-toc.json";
import {
  DOC_INDEX,
  DOC_REDIRECTS,
  DOCS,
  NAVIGATION,
  type DocPath,
} from "@/generated/docs";

export interface DocFrontmatter {
  title?: string;
  description?: string;
  order?: number;
  published?: boolean;
  group?: string;
  product?: string;
  [key: string]: unknown;
}

export interface Heading {
  id: string;
  text: string;
  level: number;
}

export interface BreadcrumbItem {
  title: string;
  path: string;
}

export interface DocSummary {
  path: string;
  title: string;
  description?: string;
  href: string;
}

export interface Doc extends DocSummary {
  content: string;
  frontmatter: DocFrontmatter;
  headings: Heading[];
  packageId?: string;
  section: string;
  breadcrumbs: BreadcrumbItem[];
  prev?: DocSummary;
  next?: DocSummary;
}

export interface DocItem extends DocSummary {
  packageId?: string;
  children?: DocItem[];
}

export interface DocSection {
  title: string;
  description?: string;
  items: DocItem[];
}

interface RawNavigationItem {
  readonly title: string;
  readonly path: string;
  readonly source: string;
  readonly package?: string;
  readonly children?: readonly RawNavigationItem[];
}

const DOC_TOCS = tocData as Partial<Record<DocPath, Heading[]>>;

export function hrefForDocPath(path: string): string {
  return path ? `/docs/${path}` : "/docs";
}

function indexRecord(path: string) {
  return DOC_INDEX.find((entry) => entry.path === path);
}

function navigationItemToDocItem(
  item: RawNavigationItem,
  inheritedPackage?: string,
): DocItem {
  const record = indexRecord(item.path);
  const packageId = item.package ?? inheritedPackage ?? record?.package ?? undefined;
  return {
    path: item.path,
    title: record?.title ?? item.title,
    ...(record?.description ? { description: record.description } : {}),
    href: hrefForDocPath(item.path),
    ...(packageId ? { packageId } : {}),
    ...(item.children?.length
      ? {
          children: item.children.map((child) =>
            navigationItemToDocItem(child, packageId),
          ),
        }
      : {}),
  };
}

export function getDocsNavigation(): DocSection[] {
  return NAVIGATION.sections.map((section) => ({
    title: section.title,
    ...(section.description ? { description: section.description } : {}),
    items: section.items.map((item) => navigationItemToDocItem(item)),
  }));
}

export function flattenDocItems(items: readonly DocItem[]): DocItem[] {
  return items.flatMap((item) => [
    item,
    ...(item.children ? flattenDocItems(item.children) : []),
  ]);
}

export function getAllDocs(): DocItem[] {
  const home = navigationItemToDocItem(NAVIGATION.home);
  return [
    home,
    ...getDocsNavigation().flatMap((section) => flattenDocItems(section.items)),
  ];
}

function findDocItem(items: readonly DocItem[], path: string): DocItem | undefined {
  for (const item of items) {
    if (item.path === path) return item;
    const child = item.children ? findDocItem(item.children, path) : undefined;
    if (child) return child;
  }
  return undefined;
}

export function getPackageRoot(path: string): DocItem | undefined {
  const segments = path.split("/");
  if (segments[0] !== "packages" || !segments[1]) return undefined;
  const packagePath = `packages/${segments[1]}`;
  const packageSection = getDocsNavigation().find(
    (section) => section.title === "Packages",
  );
  return packageSection
    ? findDocItem(packageSection.items, packagePath)
    : undefined;
}

function getNavigationScope(path: string): DocItem[] {
  const packageRoot = getPackageRoot(path);
  if (packageRoot) return flattenDocItems([packageRoot]);

  return getDocsNavigation().flatMap((section) => {
    if (section.title !== "Packages") return flattenDocItems(section.items);
    return section.items;
  });
}

function loadDoc(path: DocPath): Doc {
  const parsed = matter(DOCS[path]);
  const frontmatter = parsed.data as DocFrontmatter;
  const record = indexRecord(path);
  const title =
    typeof frontmatter.title === "string"
      ? frontmatter.title
      : record?.title ?? path || "Codepot documentation";
  const description =
    typeof frontmatter.description === "string"
      ? frontmatter.description
      : record?.description;
  const packageId =
    typeof frontmatter.product === "string"
      ? frontmatter.product
      : record?.package ?? undefined;

  return {
    path,
    title,
    ...(description ? { description } : {}),
    href: hrefForDocPath(path),
    content: parsed.content.trim(),
    frontmatter,
    headings: DOC_TOCS[path] ?? [],
    ...(packageId ? { packageId } : {}),
    section: record?.section ?? "Documentation",
    breadcrumbs: record?.breadcrumbs
      ? [...record.breadcrumbs]
      : [{ title, path }],
  };
}

export function getDocByPath(path: string): Doc | null {
  if (!(path in DOCS)) return null;
  const doc = loadDoc(path as DocPath);
  const scope = getNavigationScope(path);
  const currentIndex = scope.findIndex((item) => item.path === path);

  return {
    ...doc,
    ...(currentIndex > 0 ? { prev: scope[currentIndex - 1] } : {}),
    ...(currentIndex >= 0 && currentIndex < scope.length - 1
      ? { next: scope[currentIndex + 1] }
      : {}),
  };
}

export function getRedirectTarget(path: string): string | null {
  return path in DOC_REDIRECTS
    ? DOC_REDIRECTS[path as keyof typeof DOC_REDIRECTS]
    : null;
}

export function generateStaticParams(): { path: string[] }[] {
  return Object.keys(DOCS).map((path) => ({
    path: path ? path.split("/") : [],
  }));
}

export function generateDocMetadata(doc: Doc): Metadata {
  const title = `${doc.title} - Codepot Documentation`;
  const description = doc.description ?? `Documentation for ${doc.title}`;
  const canonical = doc.href;

  return {
    title,
    description,
    alternates: { canonical },
    openGraph: {
      type: "article",
      title,
      description,
      url: canonical,
      siteName: "Codepot",
      images: [
        {
          url: "/opengraph-image",
          width: 1200,
          height: 630,
          alt: `${doc.title} — Codepot Documentation`,
        },
      ],
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
      images: ["/opengraph-image"],
    },
  };
}

export function searchDocs(query: string): DocItem[] {
  const tokens = query
    .trim()
    .toLowerCase()
    .split(/\s+/)
    .filter(Boolean);
  if (!tokens.length) return [];

  return DOC_INDEX.filter((item) =>
    tokens.every((token) => item.searchText.includes(token)),
  ).map((item) => ({
    path: item.path,
    title: item.title,
    ...(item.description ? { description: item.description } : {}),
    href: hrefForDocPath(item.path),
    ...(item.package ? { packageId: item.package } : {}),
  }));
}
