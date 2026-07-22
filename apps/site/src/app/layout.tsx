import type { Metadata, Viewport } from 'next';
import { Inter, JetBrains_Mono } from 'next/font/google';

import { SiteHeader } from '@/components/site-header';

import './globals.css';

const sans = Inter({ subsets: ['latin'], variable: '--font-sans' });
const mono = JetBrains_Mono({ subsets: ['latin'], variable: '--font-mono' });

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL ?? 'https://codepot.dev'),
  title: {
    default: 'Codepot — typed authoring and safe code generation',
    template: '%s · Codepot',
  },
  description: 'Author typed contracts once, validate reusable Handlebars template packs, and generate deterministic source code safely.',
  openGraph: {
    title: 'Codepot',
    description: 'Typed authoring, reusable template packs, and production-grade code generation.',
    type: 'website',
  },
};

export const viewport: Viewport = {
  colorScheme: 'dark light',
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#f7f8fb' },
    { media: '(prefers-color-scheme: dark)', color: '#080b12' },
  ],
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${sans.variable} ${mono.variable}`}>
      <body>
        <SiteHeader />
        {children}
        <footer className="site-footer">
          <span>Codepot</span>
          <span>Typed contracts. Reusable templates. Safe generation.</span>
        </footer>
      </body>
    </html>
  );
}
