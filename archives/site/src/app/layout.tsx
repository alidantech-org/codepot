import type { Metadata } from "next";
import { Inter, Sora, JetBrains_Mono } from "next/font/google";
import { GoogleAnalytics } from "@next/third-parties/google";
import { ThemeProvider } from "next-themes";
import { NavBar } from "@/components/layout/NavBar";
import { Footer } from "@/components/layout/Footer";
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

const fontMono = JetBrains_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Codepurify - Semantic Metadata Inference Engine",
  description:
    "Template compiler for generating architecture artifacts from typed domain configs. Define facts about your domain, and Codepurify infers query capabilities, mutation semantics, relation groups, workflows, and validation rules.",
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
    apple: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${fontSans.variable} ${fontHeading.variable} ${fontMono.variable} h-full antialiased`}
      suppressHydrationWarning
    >
      <body className="min-h-full flex flex-col bg-background text-foreground">
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <div className="flex min-h-screen flex-col">
            {/* Background grid */}
            <div className="pointer-events-none fixed inset-0 z-0 bg-grid" />

            {/* Glow orbs */}
            <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
              <div
                className="absolute -left-32 -top-32 h-[600px] w-[600px] rounded-full opacity-20 bg-glow-blue"
                style={{
                  filter: "blur(80px)",
                }}
              />
              <div
                className="absolute -right-48 top-1/3 h-[500px] w-[500px] rounded-full opacity-15 bg-glow-purple"
                style={{
                  filter: "blur(80px)",
                }}
              />
              <div
                className="absolute bottom-24 left-1/3 h-[400px] w-[400px] rounded-full opacity-10 bg-glow-teal"
                style={{
                  filter: "blur(80px)",
                }}
              />
            </div>

            <NavBar />
            <main className="relative z-10 w-full flex-1">{children}</main>
            <Footer />
          </div>
        </ThemeProvider>
        <GoogleAnalytics gaId="G-72Q0YQE17J" />
      </body>
    </html>
  );
}
