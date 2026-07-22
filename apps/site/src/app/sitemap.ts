import type { MetadataRoute } from "next";

import { getAllDocs } from "@/lib/docs";

export default function sitemap(): MetadataRoute.Sitemap {
  const origin = process.env.NEXT_PUBLIC_SITE_URL ?? "https://codepot.dev";
  const now = new Date();
  return [
    { url: origin, lastModified: now, changeFrequency: "weekly", priority: 1 },
    { url: `${origin}/docs`, lastModified: now, changeFrequency: "weekly", priority: 0.9 },
    ...getAllDocs().map((doc) => ({
      url: `${origin}/docs/${doc.slug}`,
      lastModified: now,
      changeFrequency: "weekly" as const,
      priority: 0.7,
    })),
  ];
}
