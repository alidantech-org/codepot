import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { DocsBreadcrumbs } from "@/components/docs/DocsBreadcrumbs";
import { DocsPager } from "@/components/docs/DocsPager";
import { DocsToc } from "@/components/docs/DocsToc";
import { MarkdownRenderer } from "@/components/docs/MarkdownRenderer";
import { ProductBar } from "@/components/docs/ProductBar";
import { generateDocMetadata, getDocByPath } from "@/lib/docs";

interface DocPageProps {
  params: Promise<{ path?: string[] }>;
}

// Documentation content and navigation are compiled into the server bundle.
// Resolve every requested path directly from that bundled index instead of
// creating a Next.js static fallback route for the optional catch-all segment.
// Unknown paths still reach notFound() below.
export const dynamic = "force-dynamic";

function resolvePath(path: string[] | undefined): string {
  return path?.join("/") ?? "";
}

export async function generateMetadata({ params }: DocPageProps): Promise<Metadata> {
  const path = resolvePath((await params).path);
  const page = getDocByPath(path);
  if (!page) {
    return {
      title: "Not Found - Codepot Documentation",
      description: "The requested documentation page was not found.",
    };
  }
  return generateDocMetadata(page);
}

export default async function DocPage({ params }: DocPageProps) {
  const path = resolvePath((await params).path);
  const page = getDocByPath(path);
  if (!page) notFound();

  const tocHeadings = page.headings.filter(
    (heading) => heading.level >= 2 && heading.level <= 3,
  );

  return (
    <div
      className={`mx-auto grid w-full min-w-0 max-w-[1240px] grid-cols-1 gap-8 px-4 py-7 sm:px-6 lg:px-8 xl:items-start ${
        tocHeadings.length
          ? "xl:grid-cols-[minmax(0,1fr)_15rem] xl:gap-10"
          : "xl:grid-cols-1"
      }`}
    >
      <article className="min-w-0">
        <DocsBreadcrumbs items={page.breadcrumbs} />

        {page.packageId && <ProductBar productId={page.packageId} />}

        {tocHeadings.length > 0 && (
          <details className="mb-7 border-y border-border bg-card/35 px-4 py-3 xl:hidden">
            <summary className="cursor-pointer text-sm font-semibold text-foreground">
              On this page
            </summary>
            <nav
              aria-label="Mobile table of contents"
              className="mt-3 grid gap-0.5 border-t border-border/70 pt-3"
            >
              {tocHeadings.map((heading) => (
                <a
                  key={heading.id}
                  href={`#${heading.id}`}
                  className={`border-l-2 border-border py-1.5 pr-2 text-sm text-muted-foreground transition-colors hover:border-primary hover:text-foreground ${
                    heading.level === 3 ? "pl-6" : "pl-3 font-medium"
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

      {tocHeadings.length > 0 && (
        <aside className="sticky top-20 hidden max-h-[calc(100dvh-6rem)] self-start overflow-y-auto border-l border-border/70 pl-5 xl:block scrollbar-thin">
          <DocsToc headings={page.headings} />
        </aside>
      )}
    </div>
  );
}
