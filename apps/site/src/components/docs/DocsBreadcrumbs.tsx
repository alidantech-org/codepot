import Link from "next/link";
import { ChevronRight } from "lucide-react";

import type { BreadcrumbItem } from "@/lib/docs";

export function DocsBreadcrumbs({ items }: { items: BreadcrumbItem[] }) {
  const normalized = items.filter((item, index, all) => {
    if (index === all.length - 1) return true;
    return item.path !== all[index + 1]?.path;
  });

  return (
    <nav aria-label="Breadcrumb" className="mb-5 overflow-x-auto pb-1 scrollbar-thin">
      <ol className="flex min-w-max items-center gap-1.5 text-xs text-muted-foreground">
        <li>
          <Link href="/docs" className="transition-colors hover:text-foreground">
            Docs
          </Link>
        </li>
        {normalized
          .filter((item) => item.path !== "")
          .map((item, index, visibleItems) => {
            const current = index === visibleItems.length - 1;
            return (
              <li key={item.path} className="flex items-center gap-1.5">
                <ChevronRight className="h-3 w-3 shrink-0 text-border" aria-hidden="true" />
                {current ? (
                  <span className="max-w-[15rem] truncate font-medium text-foreground" aria-current="page">
                    {item.title}
                  </span>
                ) : (
                  <Link
                    href={item.path ? `/docs/${item.path}` : "/docs"}
                    className="max-w-[13rem] truncate transition-colors hover:text-foreground"
                  >
                    {item.title}
                  </Link>
                )}
              </li>
            );
          })}
      </ol>
    </nav>
  );
}
