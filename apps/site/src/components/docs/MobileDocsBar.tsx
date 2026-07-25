"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ChevronLeft, ChevronRight, List, X } from "lucide-react";
import { useMemo, useState } from "react";

import { DocsSidebar } from "@/components/docs/DocsSidebar";
import type { DocItem, DocSection } from "@/lib/docs";

function docPathFromPathname(pathname: string): string {
  if (pathname === "/docs") return "";
  return decodeURIComponent(pathname.replace(/^\/docs\/?/, "").replace(/\/$/, ""));
}

function flatten(items: readonly DocItem[]): DocItem[] {
  return items.flatMap((item) => [item, ...(item.children ? flatten(item.children) : [])]);
}

function findPackageRoot(sections: DocSection[], path: string): DocItem | undefined {
  const segments = path.split("/");
  if (segments[0] !== "packages" || !segments[1]) return undefined;
  const packagePath = `packages/${segments[1]}`;
  const packagesSection = sections.find((section) => section.title === "Packages");
  const directory = packagesSection?.items.find((item) => item.path === "packages");
  return directory?.children?.find((item) => item.path === packagePath);
}

function navigationScope(sections: DocSection[], path: string): DocItem[] {
  const packageRoot = findPackageRoot(sections, path);
  if (packageRoot) return flatten([packageRoot]);

  return sections.flatMap((section) =>
    section.title === "Packages" ? section.items : flatten(section.items),
  );
}

export function MobileDocsBar({ sections }: { sections: DocSection[] }) {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();
  const currentPath = docPathFromPathname(pathname);
  const scope = useMemo(
    () => navigationScope(sections, currentPath),
    [sections, currentPath],
  );
  const currentIndex = scope.findIndex((doc) => doc.path === currentPath);
  const previousDoc = currentIndex > 0 ? scope[currentIndex - 1] : null;
  const nextDoc =
    currentIndex >= 0 && currentIndex < scope.length - 1
      ? scope[currentIndex + 1]
      : null;
  const packageRoot = findPackageRoot(sections, currentPath);

  return (
    <>
      <div className="sticky top-15 z-20 border-b border-border bg-background/92 backdrop-blur-xl lg:hidden">
        <div className="flex h-13 items-center justify-between px-3 sm:px-4">
          <button
            type="button"
            onClick={() => setOpen(true)}
            className="flex min-w-0 items-center gap-2 px-1 py-1 text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            <List className="h-4 w-4 shrink-0" />
            <span className="truncate">{packageRoot?.title ?? "Documentation"}</span>
          </button>
          <div className="flex items-center gap-1">
            {previousDoc ? (
              <Link
                href={previousDoc.href}
                aria-label={`Previous: ${previousDoc.title}`}
                className="inline-flex h-8 w-8 items-center justify-center text-muted-foreground transition-colors hover:bg-card-muted hover:text-foreground"
              >
                <ChevronLeft className="h-4 w-4" />
              </Link>
            ) : (
              <span className="inline-flex h-8 w-8 items-center justify-center text-muted-foreground/25">
                <ChevronLeft className="h-4 w-4" />
              </span>
            )}
            {nextDoc ? (
              <Link
                href={nextDoc.href}
                aria-label={`Next: ${nextDoc.title}`}
                className="inline-flex h-8 w-8 items-center justify-center text-muted-foreground transition-colors hover:bg-card-muted hover:text-foreground"
              >
                <ChevronRight className="h-4 w-4" />
              </Link>
            ) : (
              <span className="inline-flex h-8 w-8 items-center justify-center text-muted-foreground/25">
                <ChevronRight className="h-4 w-4" />
              </span>
            )}
          </div>
        </div>
      </div>

      {open && (
        <div className="fixed inset-0 z-[200] lg:hidden">
          <button
            type="button"
            aria-label="Close documentation menu"
            className="fixed inset-0 bg-black/50 backdrop-blur-[2px]"
            onClick={() => setOpen(false)}
          />
          <aside className="fixed left-0 top-0 z-[210] flex h-dvh w-[21rem] max-w-[88vw] flex-col border-r border-border bg-background shadow-2xl">
            <div className="flex h-15 shrink-0 items-center justify-between border-b border-border px-4">
              <div className="min-w-0">
                <p className="font-mono text-[9px] uppercase tracking-[0.16em] text-muted-foreground">
                  Codepot
                </p>
                <h2 className="truncate text-sm font-semibold text-foreground">
                  {packageRoot?.title ?? "Documentation"}
                </h2>
              </div>
              <button
                type="button"
                onClick={() => setOpen(false)}
                aria-label="Close documentation menu"
                className="inline-flex h-8 w-8 items-center justify-center text-muted-foreground transition-colors hover:bg-card-muted hover:text-foreground"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <div className="min-h-0 flex-1 overflow-y-auto overflow-x-hidden scrollbar-thin">
              <DocsSidebar sections={sections} onNavigate={() => setOpen(false)} />
            </div>
          </aside>
        </div>
      )}
    </>
  );
}
