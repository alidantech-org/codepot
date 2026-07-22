import matter from 'gray-matter';

import { DOCS, NAVIGATION, type DocSlug } from '@/generated/docs';

export interface DocMetadata {
  readonly title: string;
  readonly description: string;
  readonly order: number;
}

export interface DocRecord {
  readonly slug: DocSlug;
  readonly metadata: DocMetadata;
  readonly content: string;
}

export interface NavigationItem {
  readonly title: string;
  readonly slug: DocSlug;
}

export interface NavigationSection {
  readonly title: string;
  readonly items: readonly NavigationItem[];
}

/** Parsed docs are stable build inputs generated from the root docs directory. */
export function getDoc(slug: string): DocRecord | undefined {
  if (!(slug in DOCS)) return undefined;
  const typedSlug = slug as DocSlug;
  const parsed = matter(DOCS[typedSlug]);
  return {
    slug: typedSlug,
    metadata: {
      title: String(parsed.data.title ?? typedSlug),
      description: String(parsed.data.description ?? ''),
      order: Number(parsed.data.order ?? 0),
    },
    content: parsed.content,
  };
}

export function getAllDocs(): readonly DocRecord[] {
  return Object.keys(DOCS)
    .map((slug) => getDoc(slug))
    .filter((doc): doc is DocRecord => Boolean(doc))
    .sort((left, right) => left.metadata.order - right.metadata.order || left.slug.localeCompare(right.slug));
}

export function getNavigation(): readonly NavigationSection[] {
  return NAVIGATION.sections.map((section) => ({
    title: section.title,
    items: section.items.filter((item): item is NavigationItem => item.slug in DOCS),
  }));
}

export function adjacentDocs(slug: string): {
  readonly previous?: DocRecord;
  readonly next?: DocRecord;
} {
  const docs = getAllDocs();
  const index = docs.findIndex((doc) => doc.slug === slug);
  return {
    ...(index > 0 ? { previous: docs[index - 1] } : {}),
    ...(index >= 0 && index < docs.length - 1 ? { next: docs[index + 1] } : {}),
  };
}
