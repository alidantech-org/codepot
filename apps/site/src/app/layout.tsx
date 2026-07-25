import type { Metadata } from "next";
import { Inter, JetBrains_Mono, Playfair_Display, Sora } from "next/font/google";
import { ThemeProvider } from "next-themes";

import { Footer } from "@/components/layout/Footer";
import { NavBar } from "@/components/layout/NavBar";

import "./globals.css";

const fontSans = Inter({
  variable: "--font-sans",
  subsets: ["latin"],
  display: "swap",
});
const fontHeading = Sora({
  variable: "--font-heading",
  subsets: ["latin"],
  display: "swap",
});
const fontDisplay = Playfair_Display({
  variable: "--font-display",
  subsets: ["latin"],
  display: "swap",
});
const fontMono = JetBrains_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
  display: "swap",
});

const siteUrl =
  process.env.NEXT_PUBLIC_SITE_URL ?? "https://code.alidantech.org";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  applicationName: "Codepot",
  title: {
    default: "Codepot — typed software intent and reusable generation",
    template: "%s — Codepot",
  },
  description:
    "Codepot connects supported OpenAPI and Jinja packages, an official JavaScript runtime, and a final Rust language platform for developers, tools, and AI agents.",
  keywords: [
    "Codepot",
    "code generation",
    "OpenAPI",
    "template packs",
    "developer tooling",
    "TypeScript",
    "Python",
    "Rust",
    "language server",
    "MCP",
  ],
  authors: [{ name: "Alidantech", url: "https://github.com/alidantech-org" }],
  creator: "Alidantech",
  publisher: "Alidantech",
  category: "Developer Tools",
  alternates: {
    canonical: "/",
  },
  icons: {
    icon: [
      { url: "/favicon.svg", type: "image/svg+xml" },
      { url: "/icon.svg", type: "image/svg+xml" },
    ],
    shortcut: "/favicon.svg",
  },
  openGraph: {
    type: "website",
    locale: "en_US",
    url: siteUrl,
    siteName: "Codepot",
    title: "Codepot — typed software intent and reusable generation",
    description:
      "Move proven contract and generation ideas from supported prototypes into a frontend-neutral runtime and a complete Rust language platform.",
    images: [
      {
        url: "/opengraph-image",
        width: 1200,
        height: 630,
        alt: "Codepot African code pot mark and developer tooling platform",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Codepot — typed software intent and reusable generation",
    description:
      "Supported OpenAPI and Jinja tools, an official JavaScript runtime, and the final Rust Codepot platform.",
    images: ["/opengraph-image"],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-image-preview": "large",
      "max-snippet": -1,
      "max-video-preview": -1,
    },
  },
};

const structuredData = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "WebSite",
      "@id": `${siteUrl}/#website`,
      url: siteUrl,
      name: "Codepot",
      description:
        "Typed software intent, reusable template packs, safe generation, and language tooling.",
      publisher: { "@id": `${siteUrl}/#organization` },
    },
    {
      "@type": "Organization",
      "@id": `${siteUrl}/#organization`,
      name: "Alidantech",
      url: "https://github.com/alidantech-org",
      logo: `${siteUrl}/logo.svg`,
    },
    {
      "@type": "SoftwareApplication",
      "@id": `${siteUrl}/#software`,
      name: "Codepot",
      applicationCategory: "DeveloperApplication",
      operatingSystem: "Cross-platform",
      url: siteUrl,
      codeRepository: "https://github.com/alidantech-org/codepot",
      license: "https://opensource.org/license/mit",
      description:
        "A complementary ecosystem for typed contracts, template packs, safe generation, reusable runtimes, and language tooling.",
    },
  ],
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html
      lang="en"
      className={`${fontSans.variable} ${fontHeading.variable} ${fontDisplay.variable} ${fontMono.variable} h-full antialiased`}
      suppressHydrationWarning
    >
      <body className="min-h-full bg-background text-foreground">
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
        />
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <div className="flex min-h-screen flex-col">
            <div className="pointer-events-none fixed inset-0 z-0 bg-grid opacity-70" />
            <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
              <div className="absolute -left-32 -top-32 h-[600px] w-[600px] rounded-full bg-glow-clay opacity-25 blur-[90px]" />
              <div className="absolute -right-48 top-1/3 h-[500px] w-[500px] rounded-full bg-glow-amber opacity-20 blur-[90px]" />
              <div className="absolute bottom-24 left-1/3 h-[400px] w-[400px] rounded-full bg-glow-sand opacity-15 blur-[80px]" />
            </div>
            <NavBar />
            <main className="relative z-10 w-full flex-1">{children}</main>
            <Footer />
          </div>
        </ThemeProvider>
      </body>
    </html>
  );
}
