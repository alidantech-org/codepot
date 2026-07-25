import type { Metadata } from "next";
import type { ReactNode } from "react";

import { DocsSidebar } from "@/components/docs/DocsSidebar";
import { MobileDocsBar } from "@/components/docs/MobileDocsBar";
import { getAllDocs } from "@/lib/docs";

export const metadata: Metadata = {
  title: "Documentation - Codepot",
  description: "Documentation for codepot-openapi, codepotg, codepotx, codepotx-cli, Codepot Lang, and the final Codepot platform.",
  alternates: {
    canonical: "/docs",
  },
  openGraph: {
    type: "website",
    title: "Codepot Documentation",
    description: "Guides, concepts, package references, and platform documentation for the complete Codepot ecosystem.",
    url: "/docs",
    siteName: "Codepot",
    images: [
      {
        url: "/opengraph-image",
        width: 1200,
        height: 630,
        alt: "Codepot Documentation",
      },
    ],
  },
};

export default function DocsLayout({ children }: Readonly<{ children: ReactNode }>) {
  const docs = getAllDocs();

  return (
    <>
      <MobileDocsBar docs={docs} />
      <div className="relative flex w-full gap-6 bg-background">
        <aside className="sticky top-15 z-30 hidden h-[calc(100dvh-4rem)] w-[260px] shrink-0 overflow-y-auto overflow-x-hidden border-r border-border bg-background lg:block scrollbar-thin">
          <DocsSidebar docs={docs} />
        </aside>
        <main className="min-w-0 flex-1 py-8">
          <div className="mx-auto max-w-5xl">{children}</div>
        </main>
        <aside className="sticky top-15 z-20 hidden h-[calc(100dvh-4rem)] w-[240px] shrink-0 overflow-y-auto overflow-x-hidden border-l border-border bg-background pl-4 xl:block scrollbar-thin">
          <div id="toc-placeholder" />
        </aside>
      </div>
    </>
  );
}
