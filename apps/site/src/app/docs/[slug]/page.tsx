import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { DocsPager } from "@/components/docs/DocsPager";
import { MarkdownRenderer } from "@/components/docs/MarkdownRenderer";
import { TocRenderer } from "@/components/docs/TocRenderer";
import {
  generateDocMetadata,
  generateStaticParams as generatePublicDocParams,
  getDocBySlug,
} from "@/lib/docs";

interface DocPageProps {
  params: Promise<{ slug: string }>;
}

export const dynamicParams = false;

export function generateStaticParams(): { slug: string }[] {
  return generatePublicDocParams();
}

export async function generateMetadata({ params }: DocPageProps): Promise<Metadata> {
  const { slug } = await params;
  const page = getDocBySlug(slug);
  if (!page) {
    return {
      title: "Not Found - Codepot Documentation",
      description: "The requested documentation page was not found.",
    };
  }
  return generateDocMetadata(page);
}

export default async function DocPage({ params }: DocPageProps) {
  const { slug } = await params;
  const page = getDocBySlug(slug);
  if (!page) notFound();

  return (
    <>
      <TocRenderer headings={page.headings} />
      <article className="mx-auto w-full max-w-3xl px-4 py-8 md:px-6 lg:py-10">
        <MarkdownRenderer content={page.content} />
        <DocsPager doc={page} />
      </article>
    </>
  );
}
