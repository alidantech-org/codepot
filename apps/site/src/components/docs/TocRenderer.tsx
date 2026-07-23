"use client";

import { useSyncExternalStore } from "react";
import { createPortal } from "react-dom";

import { DocsToc } from "@/components/docs/DocsToc";
import type { Heading } from "@/lib/docs";

function subscribeToContainer(): () => void {
  return () => undefined;
}

function getClientContainer(): HTMLElement | null {
  return document.getElementById("toc-placeholder");
}

function getServerContainer(): null {
  return null;
}

export function TocRenderer({ headings }: { headings: Heading[] }) {
  const container = useSyncExternalStore(
    subscribeToContainer,
    getClientContainer,
    getServerContainer,
  );

  if (!container || headings.length === 0) return null;
  return createPortal(<DocsToc headings={headings} />, container);
}
