import type { MetadataRoute } from "next";

import { getAllDocs } from "@/lib/docs";

export default function sitemap(): MetadataRoute.Sitemap {
  const origin = process.env.NEXT_PUBLIC_SITE_URL ?? "https://code.alidantech.org";
  const now = new Date();
  const docs = getAllDocs();

  return [
    { url: origin, lastModified: now, changeFrequency: "weekly", priority: 1 },
    ...docs.map((doc) => ({
      url: `${origin}${doc.href}`,
      lastModified: now,
      changeFrequency: "weekly" as const,
      priority: doc.path === "" ? 0.9 : doc.path === "packages" ? 0.85 : 0.7,
    })),
  ];
}
