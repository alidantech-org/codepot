"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import type { DocItem } from "@/lib/docs";

interface DocsSidebarProps {
  docs: DocItem[];
  className?: string;
  onNavigate?: () => void;
}

interface SidebarLinkProps {
  doc: DocItem;
  pathname: string;
  onNavigate?: () => void;
  depth?: number;
}

function SidebarLink({
  doc,
  pathname,
  onNavigate,
  depth = 0,
}: SidebarLinkProps) {
  const isActive = pathname === `/docs/${doc.slug}`;
  const hasChildren = doc.children && doc.children.length > 0;
  const isChildActive = doc.children?.some(
    (child) => pathname === `/docs/${child.slug}`,
  );

  return (
    <div>
      <Link
        href={`/docs/${doc.slug}`}
        onClick={onNavigate}
        className={cn(
          "group relative text-foreground flex items-center gap-2 rounded-md px-3 py-1.5 text-sm transition-all duration-150",
          depth > 0 &&
            "ml-3 border-l border-border pl-4 rounded-none rounded-r-md",
          isActive
            ? "bg-primary/10 text-primary font-medium"
            : "text-muted-foreground/70 hover:text-foreground hover:bg-muted/60",
        )}
      >
        {isActive && (
          <span className="absolute left-0 top-1 bottom-1 w-0.5 rounded-full bg-primary" />
        )}

        <span className="flex-1 truncate">{doc.title}</span>

        {hasChildren && (
          <ChevronRight
            className={cn(
              "h-3.5 w-3.5 shrink-0 text-muted-foreground/50 transition-transform duration-200",
              isChildActive && "rotate-90",
            )}
          />
        )}
      </Link>

      {hasChildren && (isActive || isChildActive) && (
        <div className="mt-0.5 space-y-0.5">
          {doc.children!.map((child) => (
            <SidebarLink
              key={child.slug}
              doc={child}
              pathname={pathname}
              onNavigate={onNavigate}
              depth={depth + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export function DocsSidebar({ docs, className, onNavigate }: DocsSidebarProps) {
  const pathname = usePathname();

  const grouped = docs.reduce(
    (acc, doc) => {
      const group = doc.group || "__ungrouped__";
      acc[group] ??= [];
      acc[group].push(doc);
      return acc;
    },
    {} as Record<string, DocItem[]>,
  );

  return (
    <nav className={cn("space-y-6 px-4 py-6", className)}>
      {Object.entries(grouped).map(([group, groupDocs]) => {
        if (group === "__ungrouped__") {
          return (
            <div key={group} className="space-y-0.5">
              {groupDocs.map((doc) => (
                <SidebarLink
                  key={doc.slug}
                  doc={doc}
                  pathname={pathname}
                  onNavigate={onNavigate}
                />
              ))}
            </div>
          );
        }

        return (
          <div key={group} className="space-y-0.5">
            <div className="mb-3 px-3 pb-2">
              <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                {group}
              </p>
              <div className="mt-1.5 h-px bg-border" />
            </div>

            {groupDocs.map((doc) => (
              <SidebarLink
                key={doc.slug}
                doc={doc}
                pathname={pathname}
                onNavigate={onNavigate}
              />
            ))}
          </div>
        );
      })}
    </nav>
  );
}
