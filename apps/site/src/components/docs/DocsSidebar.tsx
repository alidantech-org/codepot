"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ChevronDown, ChevronLeft, PackageOpen } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import type { DocItem, DocSection } from "@/lib/docs";
import { cn } from "@/lib/utils";

interface DocsSidebarProps {
  sections: DocSection[];
  className?: string;
  onNavigate?: () => void;
}

function docPathFromPathname(pathname: string): string {
  if (pathname === "/docs") return "";
  return decodeURIComponent(pathname.replace(/^\/docs\/?/, "").replace(/\/$/, ""));
}

function containsPath(item: DocItem, path: string): boolean {
  return item.path === path || Boolean(item.children?.some((child) => containsPath(child, path)));
}

function findPackageRoot(sections: DocSection[], path: string): DocItem | undefined {
  const segments = path.split("/");
  if (segments[0] !== "packages" || !segments[1]) return undefined;
  const packagePath = `packages/${segments[1]}`;
  const packagesSection = sections.find((section) => section.title === "Packages");
  const directory = packagesSection?.items.find((item) => item.path === "packages");
  return directory?.children?.find((item) => item.path === packagePath);
}

function SidebarNode({
  item,
  currentPath,
  expanded,
  onToggle,
  onNavigate,
  depth = 0,
  labelOverride,
}: {
  item: DocItem;
  currentPath: string;
  expanded: Set<string>;
  onToggle: (path: string) => void;
  onNavigate?: () => void;
  depth?: number;
  labelOverride?: string;
}) {
  const active = currentPath === item.path;
  const branchActive = containsPath(item, currentPath);
  const hasChildren = Boolean(item.children?.length);
  const open = branchActive || expanded.has(item.path);

  return (
    <div className="min-w-0">
      <div
        className={cn(
          "group relative flex min-h-9 items-center border-l-2 transition-colors",
          active
            ? "border-primary bg-primary/8 text-primary"
            : "border-transparent text-muted-foreground hover:border-border hover:bg-card-muted/55 hover:text-foreground",
          depth > 0 && "ml-3",
        )}
      >
        <Link
          href={item.href}
          onClick={onNavigate}
          aria-current={active ? "page" : undefined}
          className={cn(
            "min-w-0 flex-1 truncate px-3 py-2 text-[13px] leading-5",
            active && "font-medium",
          )}
        >
          {labelOverride ?? item.title}
        </Link>
        {hasChildren && (
          <button
            type="button"
            onClick={() => onToggle(item.path)}
            aria-label={`${open ? "Collapse" : "Expand"} ${item.title}`}
            aria-expanded={open}
            className="mr-1 inline-flex h-7 w-7 shrink-0 items-center justify-center text-muted-foreground transition-colors hover:text-foreground"
          >
            <ChevronDown
              className={cn(
                "h-3.5 w-3.5 transition-transform duration-200",
                !open && "-rotate-90",
              )}
            />
          </button>
        )}
      </div>

      {hasChildren && open && (
        <div className="mt-0.5 space-y-0.5">
          {item.children!.map((child) => (
            <SidebarNode
              key={child.path}
              item={child}
              currentPath={currentPath}
              expanded={expanded}
              onToggle={onToggle}
              onNavigate={onNavigate}
              depth={depth + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export function DocsSidebar({ sections, className, onNavigate }: DocsSidebarProps) {
  const pathname = usePathname();
  const currentPath = docPathFromPathname(pathname);
  const packageRoot = useMemo(
    () => findPackageRoot(sections, currentPath),
    [sections, currentPath],
  );
  const [expanded, setExpanded] = useState<Set<string>>(() => new Set(["packages"]));

  useEffect(() => {
    if (!packageRoot) return;
    setExpanded((current) => {
      const next = new Set(current);
      next.add(packageRoot.path);
      return next;
    });
  }, [packageRoot]);

  function toggle(path: string) {
    setExpanded((current) => {
      const next = new Set(current);
      if (next.has(path)) next.delete(path);
      else next.add(path);
      return next;
    });
  }

  if (packageRoot) {
    return (
      <nav className={cn("px-4 py-5", className)} aria-label={`${packageRoot.title} documentation`}>
        <Link
          href="/docs/packages"
          onClick={onNavigate}
          className="mb-5 inline-flex items-center gap-1.5 text-xs font-medium text-muted-foreground transition-colors hover:text-foreground"
        >
          <ChevronLeft className="h-3.5 w-3.5" />
          All packages
        </Link>

        <div className="mb-5 border-b border-border pb-4">
          <span className="mb-2 inline-flex h-8 w-8 items-center justify-center border border-primary/25 bg-primary/8 text-primary">
            <PackageOpen className="h-4 w-4" />
          </span>
          <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-muted-foreground">
            Package documentation
          </p>
          <h2 className="mt-1 truncate text-base font-semibold text-foreground">
            {packageRoot.title}
          </h2>
        </div>

        <div className="space-y-0.5">
          <SidebarNode
            item={{ ...packageRoot, children: undefined }}
            labelOverride="Overview"
            currentPath={currentPath}
            expanded={expanded}
            onToggle={toggle}
            onNavigate={onNavigate}
          />
          {packageRoot.children?.map((child) => (
            <SidebarNode
              key={child.path}
              item={child}
              currentPath={currentPath}
              expanded={expanded}
              onToggle={toggle}
              onNavigate={onNavigate}
            />
          ))}
        </div>
      </nav>
    );
  }

  return (
    <nav className={cn("space-y-7 px-4 py-5", className)} aria-label="Documentation navigation">
      {sections.map((section) => (
        <section key={section.title}>
          <div className="mb-2 px-3">
            <h2 className="text-[11px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">
              {section.title}
            </h2>
          </div>
          <div className="space-y-0.5">
            {section.items.map((item) => (
              <SidebarNode
                key={item.path}
                item={item}
                currentPath={currentPath}
                expanded={expanded}
                onToggle={toggle}
                onNavigate={onNavigate}
              />
            ))}
          </div>
        </section>
      ))}
    </nav>
  );
}
