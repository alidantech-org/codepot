import type { ReactNode } from "react";
import type { Metadata } from "next";
import { DocsSidebar } from "@/components/docs/DocsSidebar";
import { MobileDocsBar } from "@/components/docs/MobileDocsBar";
import { getAllDocs } from "@/lib/docs";

export const metadata: Metadata = {
  title: "Documentation - CodePurify",
  description:
    "Complete documentation for CodePurify semantic metadata inference engine",
};

export default async function DocsLayout({
  children,
}: Readonly<{
  children: ReactNode;
}>) {
  const docs = await getAllDocs();

  return (
    <>
      <MobileDocsBar docs={docs} />

      <div className="relative flex w-full gap-6">
        <aside className="sticky top-14 z-30 hidden h-[calc(100dvh-3.5rem)] w-[260px] shrink-0 overflow-y-auto overflow-x-hidden border-r border-border bg-background lg:block scrollbar-thin">
          <DocsSidebar docs={docs} />
        </aside>

        <main className="min-w-0 flex-1 py-8">
          <div className="mx-auto max-w-5xl">{children}</div>
        </main>

        <aside className="sticky top-14 z-20 hidden h-[calc(100dvh-3.5rem)] w-[240px] shrink-0 overflow-y-auto overflow-x-hidden border-l border-border bg-background pl-4 xl:block scrollbar-thin">
          <div id="toc-placeholder" />
        </aside>
      </div>
    </>
  );
}
