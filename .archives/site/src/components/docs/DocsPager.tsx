import Link from "next/link";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Doc } from "@/lib/docs";

interface DocsPagerProps {
  doc: Doc;
  className?: string;
}

export function DocsPager({ doc, className }: DocsPagerProps) {
  const hasNavigation = doc.prev || doc.next;

  if (!hasNavigation) {
    return null;
  }

  return (
    <div className={cn("border-t border-border pt-8 mt-16", className)}>
      <div className="flex sm:flex-row gap-4 justify-between">
        {doc.prev ? (
          <Link
            href={`/docs/${doc.prev.slug}`}
            className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors group max-w-xs"
          >
            <ChevronLeft className="h-4 w-4 shrink-0" />
            <div className="text-left">
              <div className="font-medium text-foreground group-hover:text-primary">
                {doc.prev.title}
              </div>
              <div className="text-xs">Previous</div>
            </div>
          </Link>
        ) : (
          <div /> // Spacer for alignment
        )}

        {doc.next ? (
          <Link
            href={`/docs/${doc.next.slug}`}
            className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors group max-w-xs sm:ml-auto"
          >
            <div className="text-right">
              <div className="font-medium text-foreground group-hover:text-primary">
                {doc.next.title}
              </div>
              <div className="text-xs">Next</div>
            </div>
            <ChevronRight className="h-4 w-4 shrink-0" />
          </Link>
        ) : (
          <div /> // Spacer for alignment
        )}
      </div>
    </div>
  );
}
