"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ChevronRight } from "lucide-react";

import type { DocItem } from "@/lib/docs";
import { cn } from "@/lib/utils";

interface DocsSidebarProps {
  docs: DocItem[];
  className?: string;
  onNavigate?: () => void;
}

function SidebarLink({
  doc,
  pathname,
  onNavigate,
  depth = 0,
}: {
  doc: DocItem;
  pathname: string;
  onNavigate?: () => void;
  depth?: number;
}) {
  const isActive = pathname === `/docs/${doc.slug}`;
  const hasChildren = Boolean(doc.children?.length);
  const isChildActive = doc.children?.some((child) => pathname === `/docs/${child.slug}`);

  return (
    <div>
      <Link
        href={`/docs/${doc.slug}`}
        onClick={onNavigate}
        className={cn(
          "group relative flex items-center gap-2 rounded-md px-3 py-1.5 text-sm text-foreground transition-all duration-150",
          depth > 0 && "ml-3 rounded-none rounded-r-md border-l border-border pl-4",
          isActive
            ? "bg-primary/10 font-medium text-primary"
            : "text-muted-foreground/70 hover:bg-muted/60 hover:text-foreground",
        )}
      >
        {isActive && <span className="absolute bottom-1 left-0 top-1 w-0.5 rounded-full bg-primary" />}
        <span className="flex-1 truncate">{doc.title}</span>
        {hasChildren && (
          <ChevronRight className={cn("h-3.5 w-3.5 shrink-0 text-muted-foreground/50 transition-transform duration-200", isChildActive && "rotate-90")} />
        )}
      </Link>

      {hasChildren && (isActive || isChildActive) && (
        <div className="mt-0.5 space-y-0.5">
          {doc.children!.map((child) => (
            <SidebarLink key={child.slug} doc={child} pathname={pathname} onNavigate={onNavigate} depth={depth + 1} />
          ))}
        </div>
      )}
    </div>
  );
}

export function DocsSidebar({ docs, className, onNavigate }: DocsSidebarProps) {
  const pathname = usePathname();
  const grouped = docs.reduce<Record<string, DocItem[]>>((output, doc) => {
    const group = doc.group ?? "Documentation";
    output[group] ??= [];
    output[group].push(doc);
    return output;
  }, {});

  return (
    <nav className={cn("space-y-6 px-4 py-6", className)}>
      {Object.entries(grouped).map(([group, groupDocs]) => (
        <div key={group} className="space-y-0.5">
          <div className="mb-3 px-3 pb-2">
            <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">{group}</p>
            <div className="mt-1.5 h-px bg-border" />
          </div>
          {groupDocs.map((doc) => (
            <SidebarLink key={doc.slug} doc={doc} pathname={pathname} onNavigate={onNavigate} />
          ))}
        </div>
      ))}
    </nav>
  );
}
