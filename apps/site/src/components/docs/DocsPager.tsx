import Link from "next/link";
import { ArrowLeft, ArrowRight } from "lucide-react";

import type { Doc } from "@/lib/docs";
import { cn } from "@/lib/utils";

export function DocsPager({ doc, className }: { doc: Doc; className?: string }) {
  if (!doc.prev && !doc.next) return null;

  return (
    <nav
      aria-label="Documentation pagination"
      className={cn("mt-14 grid gap-3 border-t border-border pt-6 sm:grid-cols-2", className)}
    >
      {doc.prev ? (
        <Link
          href={doc.prev.href}
          className="group min-w-0 border border-border px-4 py-4 transition-colors hover:border-primary/35 hover:bg-primary/5"
        >
          <span className="flex items-center gap-2 text-[11px] font-medium uppercase tracking-[0.12em] text-muted-foreground">
            <ArrowLeft className="h-3.5 w-3.5 transition-transform group-hover:-translate-x-0.5" />
            Previous
          </span>
          <span className="mt-2 block truncate text-sm font-semibold text-foreground group-hover:text-primary">
            {doc.prev.title}
          </span>
        </Link>
      ) : (
        <span className="hidden sm:block" />
      )}

      {doc.next ? (
        <Link
          href={doc.next.href}
          className="group min-w-0 border border-border px-4 py-4 text-right transition-colors hover:border-primary/35 hover:bg-primary/5 sm:col-start-2"
        >
          <span className="flex items-center justify-end gap-2 text-[11px] font-medium uppercase tracking-[0.12em] text-muted-foreground">
            Next
            <ArrowRight className="h-3.5 w-3.5 transition-transform group-hover:translate-x-0.5" />
          </span>
          <span className="mt-2 block truncate text-sm font-semibold text-foreground group-hover:text-primary">
            {doc.next.title}
          </span>
        </Link>
      ) : null}
    </nav>
  );
}
