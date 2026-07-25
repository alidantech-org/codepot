import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "Codepot — typed software intent and reusable generation",
    short_name: "Codepot",
    description:
      "Supported contract and generation tools, an official JavaScript runtime, and a complete Rust language platform.",
    start_url: "/",
    display: "standalone",
    background_color: "#fcf8f2",
    theme_color: "#9a562d",
    categories: ["developer tools", "productivity", "utilities"],
    icons: [
      {
        src: "/favicon.svg",
        sizes: "any",
        type: "image/svg+xml",
        purpose: "maskable",
      },
    ],
  };
}
