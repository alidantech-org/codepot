"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useMemo, useState } from "react";
import { List, ChevronLeft, ChevronRight, X } from "lucide-react";
import { DocsSidebar } from "@/components/docs/DocsSidebar";

type DocItem = {
  slug: string;
  title: string;
  description?: string;
  children?: DocItem[];
};

function flattenDocs(docs: DocItem[]): DocItem[] {
  return docs.flatMap((doc) => [
    doc,
    ...(doc.children ? flattenDocs(doc.children) : []),
  ]);
}

export function MobileDocsBar({ docs }: { docs: DocItem[] }) {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();

  const flatDocs = useMemo(() => flattenDocs(docs), [docs]);

  const currentIndex = flatDocs.findIndex(
    (doc) => pathname === `/docs/${doc.slug}`,
  );

  const previousDoc = currentIndex > 0 ? flatDocs[currentIndex - 1] : null;
  const nextDoc =
    currentIndex >= 0 && currentIndex < flatDocs.length - 1
      ? flatDocs[currentIndex + 1]
      : null;

  return (
    <>
      <div className="sticky top-14 z-[100] border-b border-border bg-background/90 backdrop-blur-xl lg:hidden">
        <div className="flex h-12 items-center justify-between px-3">
          <button
            onClick={() => setOpen(true)}
            className="flex items-center gap-2 px-2 py-1 text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            <List className="h-4 w-4" />
            Docs
          </button>

          <div className="flex items-center gap-1">
            {previousDoc ? (
              <Link
                href={`/docs/${previousDoc.slug}`}
                aria-label={`Previous: ${previousDoc.title}`}
                className="p-1 text-muted-foreground transition-colors hover:text-foreground"
              >
                <ChevronLeft className="h-4 w-4" />
              </Link>
            ) : (
              <button
                disabled
                className="p-1 text-muted-foreground/30"
                aria-label="No previous doc"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
            )}

            {nextDoc ? (
              <Link
                href={`/docs/${nextDoc.slug}`}
                aria-label={`Next: ${nextDoc.title}`}
                className="p-1 text-muted-foreground transition-colors hover:text-foreground"
              >
                <ChevronRight className="h-4 w-4" />
              </Link>
            ) : (
              <button
                disabled
                className="p-1 text-muted-foreground/30"
                aria-label="No next doc"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            )}
          </div>
        </div>
      </div>

      {open && (
        <div className="fixed inset-0 z-[200] lg:hidden">
          <button
            aria-label="Close documentation menu"
            className="fixed inset-0 bg-black/50"
            onClick={() => setOpen(false)}
          />

          <aside className="fixed left-0 top-0 z-[210] flex h-dvh w-80 max-w-[85vw] flex-col border-r border-border bg-background shadow-xl">
            <div className="flex h-14 shrink-0 items-center justify-between border-b border-border px-4">
              <h2 className="text-lg font-semibold">Documentation</h2>

              <button
                onClick={() => setOpen(false)}
                className="p-1 text-muted-foreground transition-colors hover:text-foreground"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="min-h-0 flex-1 overflow-y-auto overflow-x-hidden">
              <DocsSidebar docs={docs} onNavigate={() => setOpen(false)} />
            </div>
          </aside>
        </div>
      )}
    </>
  );
}
