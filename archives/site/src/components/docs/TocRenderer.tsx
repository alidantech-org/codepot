"use client";

import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { DocsToc } from "./DocsToc";
import type { Heading } from "@/lib/docs";

interface TocRendererProps {
  headings: Heading[];
}

export function TocRenderer({ headings }: TocRendererProps) {
  const [container, setContainer] = useState<HTMLElement | null>(null);

  useEffect(() => {
    const element = document.getElementById("toc-placeholder");
    setContainer(element);

    return () => {
      setContainer(null);
    };
  }, []);

  if (!container || headings.length === 0) {
    return null;
  }

  return createPortal(<DocsToc headings={headings} />, container);
}
