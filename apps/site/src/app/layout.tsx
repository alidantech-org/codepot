import type { Metadata } from "next";
import { Inter, JetBrains_Mono, Sora } from "next/font/google";
import { ThemeProvider } from "next-themes";

import { Footer } from "@/components/layout/Footer";
import { NavBar } from "@/components/layout/NavBar";

import "./globals.css";

const fontSans = Inter({ variable: "--font-sans", subsets: ["latin"], display: "swap" });
const fontHeading = Sora({ variable: "--font-heading", subsets: ["latin"], display: "swap" });
const fontMono = JetBrains_Mono({ variable: "--font-mono", subsets: ["latin"], display: "swap" });

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL ?? "https://codepot.dev"),
  title: {
    default: "Codepot — a reliable foundation for AI-generated software",
    template: "%s — Codepot",
  },
  description:
    "Define typed software contracts, choose reusable template packs, and generate consistent production code that gives developers and AI agents a shared source of truth.",
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
    apple: "/favicon.svg",
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html
      lang="en"
      className={`${fontSans.variable} ${fontHeading.variable} ${fontMono.variable} h-full antialiased`}
      suppressHydrationWarning
    >
      <body className="min-h-full bg-background text-foreground">
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
          <div className="flex min-h-screen flex-col">
            <div className="pointer-events-none fixed inset-0 z-0 bg-grid" />
            <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
              <div className="absolute -left-32 -top-32 h-[600px] w-[600px] rounded-full bg-glow-blue opacity-20 blur-[80px]" />
              <div className="absolute -right-48 top-1/3 h-[500px] w-[500px] rounded-full bg-glow-purple opacity-15 blur-[80px]" />
              <div className="absolute bottom-24 left-1/3 h-[400px] w-[400px] rounded-full bg-glow-teal opacity-10 blur-[80px]" />
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
