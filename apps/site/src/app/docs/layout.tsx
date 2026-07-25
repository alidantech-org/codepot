import type { Metadata } from "next";
import type { ReactNode } from "react";

import { DocsSidebar } from "@/components/docs/DocsSidebar";
import { MobileDocsBar } from "@/components/docs/MobileDocsBar";
import { getDocsNavigation } from "@/lib/docs";

export const metadata: Metadata = {
  title: "Documentation - Codepot",
  description:
    "Documentation for codepot-openapi, codepotg, codepotx, codepotx-cli, Codepot Lang, and the final Codepot platform.",
  alternates: {
    canonical: "/docs",
  },
  openGraph: {
    type: "website",
    title: "Codepot Documentation",
    description:
      "Guides, concepts, package references, and platform documentation for the complete Codepot ecosystem.",
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

export default function DocsLayout({
  children,
}: Readonly<{ children: ReactNode }>) {
  const sections = getDocsNavigation();

  return (
    <>
      <MobileDocsBar sections={sections} />
      <div className="relative flex min-h-[calc(100dvh-3.75rem)] w-full bg-background">
        <aside className="sticky top-15 z-20 hidden h-[calc(100dvh-3.75rem)] w-[17.5rem] shrink-0 overflow-y-auto overflow-x-hidden border-r border-border bg-background lg:block scrollbar-thin">
          <DocsSidebar sections={sections} />
        </aside>
        <main className="flex min-w-0 flex-1">{children}</main>
      </div>
    </>
  );
}
