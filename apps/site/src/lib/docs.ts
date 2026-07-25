import type { Metadata } from "next";
import matter from "gray-matter";

import tocData from "@/generated/docs-toc.json";
import { DOCS, NAVIGATION, type DocSlug } from "@/generated/docs";

export interface DocFrontmatter {
  title?: string;
  description?: string;
  order?: number;
  published?: boolean;
  group?: string;
  [key: string]: unknown;
}

export interface Heading {
  id: string;
  text: string;
  level: number;
}

export interface DocSummary {
  slug: string;
  title: string;
  description?: string;
}

export interface Doc extends DocSummary {
  content: string;
  frontmatter: DocFrontmatter;
  headings: Heading[];
  prev?: DocSummary;
  next?: DocSummary;
}

export interface DocItem extends DocSummary {
  group?: string;
  children?: DocItem[];
}

const DOC_TOCS = tocData as Partial<Record<DocSlug, Heading[]>>;

function loadDoc(slug: DocSlug): Doc {
  const parsed = matter(DOCS[slug]);
  const frontmatter = parsed.data as DocFrontmatter;
  return {
    slug,
    title: typeof frontmatter.title === "string" ? frontmatter.title : slug,
    ...(typeof frontmatter.description === "string" ? { description: frontmatter.description } : {}),
    content: parsed.content.trim(),
    frontmatter,
    headings: DOC_TOCS[slug] ?? [],
  };
}

export function getAllDocs(): DocItem[] {
  return NAVIGATION.sections.flatMap((section) =>
    section.items.flatMap((item) => {
      if (!(item.slug in DOCS)) return [];
      const doc = loadDoc(item.slug as DocSlug);
      return [{
        slug: doc.slug,
        title: doc.title,
        ...(doc.description ? { description: doc.description } : {}),
        group: section.title,
      }];
    }),
  );
}

export function getDocBySlug(slug: string): Doc | null {
  if (!(slug in DOCS)) return null;
  const docs = getAllDocs();
  const currentIndex = docs.findIndex((doc) => doc.slug === slug);
  const doc = loadDoc(slug as DocSlug);
  return {
    ...doc,
    ...(currentIndex > 0 ? { prev: docs[currentIndex - 1] } : {}),
    ...(currentIndex >= 0 && currentIndex < docs.length - 1 ? { next: docs[currentIndex + 1] } : {}),
  };
}

export function generateStaticParams(): { slug: string }[] {
  return Object.keys(DOCS).map((slug) => ({ slug }));
}

export function generateDocMetadata(doc: Doc): Metadata {
  const title = `${doc.title} - Codepot Documentation`;
  const description = doc.description ?? `Documentation for ${doc.title}`;
  const canonical = `/docs/${doc.slug}`;

  return {
    title,
    description,
    alternates: {
      canonical,
    },
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
  const value = query.trim().toLowerCase();
  if (!value) return [];
  return getAllDocs().filter((item) => {
    const doc = loadDoc(item.slug as DocSlug);
    return [item.title, item.description, doc.content, item.slug]
      .filter(Boolean)
      .join(" ")
      .toLowerCase()
      .includes(value);
  });
}
