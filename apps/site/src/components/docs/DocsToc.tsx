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
    const elements = filtered.map((heading) => document.getElementById(heading.id)).filter((element): element is HTMLElement => element !== null);
    if (!elements.length) return;
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries.filter((entry) => entry.isIntersecting).sort((left, right) => left.boundingClientRect.top - right.boundingClientRect.top);
        if (visible[0]?.target.id) setActiveId(visible[0].target.id);
      },
      { rootMargin: "-96px 0px -70% 0px", threshold: [0, 1] },
    );
    elements.forEach((element) => observer.observe(element));
    return () => observer.disconnect();
  }, [filtered]);

  if (!filtered.length) return null;

  function scrollToHeading(id: string) {
    const element = document.getElementById(id);
    if (!element) return;
    const top = element.getBoundingClientRect().top + window.scrollY - 88;
    window.scrollTo({ top, behavior: "smooth" });
    window.history.pushState(null, "", `#${id}`);
    setActiveId(id);
  }

  return (
    <div className={cn("h-full py-5", className)}>
      <div className="sticky top-20 space-y-8">
        <div>
          <h4 className="mb-4 text-sm font-semibold text-foreground">On this page</h4>
          <nav aria-label="Table of contents" className="max-h-[calc(100vh-8rem)] space-y-0.5 overflow-y-auto pr-2 scrollbar-thin">
            {filtered.map((heading) => {
              const isActive = activeId === heading.id;
              const isChild = heading.level === 3;
              return (
                <button
                  key={heading.id}
                  type="button"
                  onClick={() => scrollToHeading(heading.id)}
                  className={cn(
                    "block w-full rounded-md py-1.5 text-left text-sm leading-5 transition-colors hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                    isChild ? "pl-4" : "pl-0 font-medium",
                    isActive ? "text-foreground" : isChild ? "text-muted-foreground/60" : "text-muted-foreground",
                  )}
                >
                  <span className={cn("block border-l-2 px-3 transition-colors", isActive ? "border-foreground" : "border-transparent")}>{heading.text}</span>
                </button>
              );
            })}
          </nav>
        </div>
      </div>
    </div>
  );
}
