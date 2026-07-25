import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { DocsPager } from "@/components/docs/DocsPager";
import { DocsToc } from "@/components/docs/DocsToc";
import { MarkdownRenderer } from "@/components/docs/MarkdownRenderer";
import { ProductBar } from "@/components/docs/ProductBar";
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

  const productId = typeof page.frontmatter.product === "string" ? page.frontmatter.product : null;

  return (
    <div className="mx-auto grid w-full max-w-[1180px] grid-cols-1 gap-10 px-4 sm:px-6 xl:grid-cols-[minmax(0,1fr)_240px] xl:gap-12">
      <article className="min-w-0">
        {productId && <ProductBar productId={productId} />}
        <MarkdownRenderer content={page.content} />
        <DocsPager doc={page} />
      </article>

      {page.headings.some((heading) => heading.level >= 2 && heading.level <= 3) && (
        <aside className="hidden min-w-0 border-l border-border pl-5 xl:block">
          <DocsToc headings={page.headings} />
        </aside>
      )}
    </div>
  );
}
