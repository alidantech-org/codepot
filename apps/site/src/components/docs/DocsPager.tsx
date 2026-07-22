import Link from "next/link";
import { ChevronLeft, ChevronRight } from "lucide-react";

import type { Doc } from "@/lib/docs";
import { cn } from "@/lib/utils";

export function DocsPager({ doc, className }: { doc: Doc; className?: string }) {
  if (!doc.prev && !doc.next) return null;

  return (
    <div className={cn("mt-16 border-t border-border pt-8", className)}>
      <div className="flex justify-between gap-4 sm:flex-row">
        {doc.prev ? (
          <Link href={`/docs/${doc.prev.slug}`} className="group flex max-w-xs items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground">
            <ChevronLeft className="h-4 w-4 shrink-0" />
            <div className="text-left">
              <div className="font-medium text-foreground group-hover:text-primary">{doc.prev.title}</div>
              <div className="text-xs">Previous</div>
            </div>
          </Link>
        ) : <div />}

        {doc.next ? (
          <Link href={`/docs/${doc.next.slug}`} className="group flex max-w-xs items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground sm:ml-auto">
            <div className="text-right">
              <div className="font-medium text-foreground group-hover:text-primary">{doc.next.title}</div>
              <div className="text-xs">Next</div>
            </div>
            <ChevronRight className="h-4 w-4 shrink-0" />
          </Link>
        ) : <div />}
      </div>
    </div>
  );
}
