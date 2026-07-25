import type { Metadata } from 'next';
import { notFound } from 'next/navigation';

import { DocsPager } from '@/components/docs/DocsPager';
import { DocsToc } from '@/components/docs/DocsToc';
import { MarkdownRenderer } from '@/components/docs/MarkdownRenderer';
import { ProductBar } from '@/components/docs/ProductBar';
import { generateDocMetadata, generateStaticParams as generatePublicDocParams, getDocBySlug } from '@/lib/docs';

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
      title: 'Not Found - Codepot Documentation',
      description: 'The requested documentation page was not found.'
    };
  }
  return generateDocMetadata(page);
}

export default async function DocPage({ params }: DocPageProps) {
  const { slug } = await params;
  const page = getDocBySlug(slug);
  if (!page) notFound();

  const productId = typeof page.frontmatter.product === 'string' ? page.frontmatter.product : null;
  const tocHeadings = page.headings.filter((heading) => heading.level >= 2 && heading.level <= 3);

  return (
    <>
      <div className="mx-auto flex-1 grid w-full max-w-6xl w-full py-6 relative px-3 md:px-6">
        <article className="min-w-0">
          {productId && <ProductBar productId={productId} />}

          {tocHeadings.length > 0 && (
            <details className="mb-8 border-y border-border bg-card/35 px-4 py-3 xl:hidden">
              <summary className="cursor-pointer text-sm font-semibold text-foreground">On this page</summary>
              <nav aria-label="Mobile table of contents" className="mt-3 grid gap-1 pb-1">
                {tocHeadings.map((heading) => (
                  <a
                    key={heading.id}
                    href={`#${heading.id}`}
                    className={`border-l-2 border-border py-1.5 pr-2 text-sm text-muted-foreground transition-colors hover:border-primary hover:text-foreground ${
                      heading.level === 3 ? 'pl-6' : 'pl-3 font-medium'
                    }`}
                  >
                    {heading.text}
                  </a>
                ))}
              </nav>
            </details>
          )}

          <MarkdownRenderer content={page.content} />
          <DocsPager doc={page} />
        </article>
      </div>
      {tocHeadings.length > 0 && (
        <aside className="hidden top-15 sticky min-w-0 border-l border-border/50 pl-5 xl:block">
          <DocsToc headings={page.headings} />
        </aside>
      )}
    </>
  );
}
