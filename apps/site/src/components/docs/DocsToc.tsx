"use client";

import { useEffect, useMemo, useState } from "react";

import type { Heading } from "@/lib/docs";
import { cn } from "@/lib/utils";

export function DocsToc({ headings, className }: { headings: Heading[]; className?: string }) {
  const filtered = useMemo(
    () => headings.filter((heading) => heading.id && heading.text && heading.level >= 2 && heading.level <= 3),
    [headings],
  );
  const [activeId, setActiveId] = useState(filtered[0]?.id ?? "");

  useEffect(() => {
    if (!filtered.length) return;
    const elements = filtered
      .map((heading) => document.getElementById(heading.id))
      .filter((element): element is HTMLElement => element !== null);
    if (!elements.length) return;

    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((left, right) => left.boundingClientRect.top - right.boundingClientRect.top);
        if (visible[0]?.target.id) setActiveId(visible[0].target.id);
      },
      { rootMargin: "-96px 0px -70% 0px", threshold: [0, 1] },
    );

    elements.forEach((element) => observer.observe(element));
    return () => observer.disconnect();
  }, [filtered]);

  if (!filtered.length) return null;

  function handleAnchorClick(event: React.MouseEvent<HTMLAnchorElement>, id: string) {
    const element = document.getElementById(id);
    if (!element) return;

    event.preventDefault();
    element.scrollIntoView({ behavior: "smooth", block: "start" });
    window.history.pushState(null, "", `#${id}`);
    setActiveId(id);
  }

  return (
    <div className={cn("py-5", className)}>
      <div className="sticky top-20">
        <h2 className="mb-4 text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">
          On this page
        </h2>
        <nav
          aria-label="Table of contents"
          className="max-h-[calc(100dvh-8rem)] space-y-0.5 overflow-y-auto pr-2 scrollbar-thin"
        >
          {filtered.map((heading) => {
            const isActive = activeId === heading.id;
            const isChild = heading.level === 3;
            return (
              <a
                key={heading.id}
                href={`#${heading.id}`}
                onClick={(event) => handleAnchorClick(event, heading.id)}
                aria-current={isActive ? "location" : undefined}
                className={cn(
                  "block border-l-2 py-1.5 pr-2 text-sm leading-5 transition-colors hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                  isChild ? "pl-5" : "pl-3 font-medium",
                  isActive
                    ? "border-primary text-foreground"
                    : isChild
                      ? "border-transparent text-muted-foreground/65"
                      : "border-transparent text-muted-foreground",
                )}
              >
                {heading.text}
              </a>
            );
          })}
        </nav>
      </div>
    </div>
  );
}
