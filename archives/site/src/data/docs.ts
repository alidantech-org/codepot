import type { DocItem } from "@/lib/docs";

export const registeredDocs: DocItem[] = [
  // Ungrouped — appears at top
  { slug: "introduction", title: "Introduction" },

  // Getting Started
  { slug: "quickstart", title: "Quick Start", group: "Getting Started" },
  { slug: "installation", title: "Installation", group: "Getting Started" },

  // Core Concepts
  { slug: "domain-definition", title: "Domain Definition", group: "Core Concepts" },

  // Internal Docs (md folder)
  { slug: "md/context", title: "Architecture Context", group: "Internal" },
  { slug: "md/marketing", title: "Marketing Strategy", group: "Internal" },
  { slug: "md/issues", title: "Known Issues", group: "Internal" },
];
