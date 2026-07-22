// src/app/docs/[...doc]/page.tsx

import type { Metadata } from "next";
import { notFound } from "next/navigation";

import {
  generateDocMetadata,
  generateStaticParams,
  getDocBySlug,
} from "@/lib/docs";

import { MarkdownRenderer } from "@/components/docs/MarkdownRenderer";
import { DocsPager } from "@/components/docs/DocsPager";
import { TocRenderer } from "@/components/docs/TocRenderer";

interface DocPageProps {
  params: Promise<{
    doc: string[];
  }>;
}

export { generateStaticParams };

export async function generateMetadata({
  params,
}: DocPageProps): Promise<Metadata> {
  const { doc } = await params;
  const slug = doc.join("/");

  const page = await getDocBySlug(slug);

  if (!page) {
    return {
      title: "Not Found - Codepurify Documentation",
      description: "The requested documentation page was not found.",
    };
  }

  return generateDocMetadata(page);
}

export default async function DocPage({ params }: DocPageProps) {
  const { doc } = await params;
  const slug = doc.join("/");

  const page = await getDocBySlug(slug);

  if (!page) {
    notFound();
  }

  return (
    <>
      <TocRenderer headings={page.headings} />

      <article className="mx-auto w-full max-w-3xl px-4 py-8 md:px-6 lg:py-10">
        {/* <header className="mb-10 border-b border-border pb-8">
          <p className="mb-3 font-mono text-xs uppercase tracking-widest text-primary">
            Documentation
          </p>

          <h1 className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
            {page.title}
          </h1>

          {page.description && (
            <p className="mt-4 text-lg leading-8 text-muted-foreground">
              {page.description}
            </p>
          )}
        </header> */}

        <MarkdownRenderer content={page.content} />

        <DocsPager doc={page} />
      </article>
    </>
  );
}
