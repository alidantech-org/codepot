"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ChevronRight } from "lucide-react";

export function DocsBreadcrumb() {
  const pathname = usePathname();

  const getBreadcrumbItems = () => {
    const segments = pathname.split("/").filter(Boolean);
    const items = [{ title: "Documentation", href: "/docs" }];

    if (
      segments.length > 1 ||
      (segments.length === 1 && segments[0] !== "docs")
    ) {
      const currentPath = segments[segments.length - 1];
      const formattedTitle = currentPath
        .split("-")
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(" ");

      items.push({
        title: formattedTitle,
        href: pathname,
      });
    }

    return items;
  };

  const items = getBreadcrumbItems();

  return (
    <nav
      className="flex items-center gap-1 text-sm text-muted-foreground mb-8"
      aria-label="Breadcrumb"
    >
      {items.map((item, index) => (
        <div key={item.href} className="flex items-center gap-1">
          {index > 0 && <ChevronRight className="h-4 w-4 shrink-0" />}
          {index === items.length - 1 ? (
            <span className="text-foreground font-medium" aria-current="page">
              {item.title}
            </span>
          ) : (
            <Link
              href={item.href}
              className="transition-colors hover:text-foreground"
            >
              {item.title}
            </Link>
          )}
        </div>
      ))}
    </nav>
  );
}
