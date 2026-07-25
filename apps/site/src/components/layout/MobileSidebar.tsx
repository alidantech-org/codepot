"use client";

import Image from "next/image";
import Link from "next/link";
import { BookOpen, Boxes, Languages, X } from "lucide-react";

import { GitHubIcon } from "@/components/icons/GitHubIcon";
import { ThemeToggle } from "@/components/theme-toggle";

interface MobileSidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const links = [
  { label: "Docs", href: "/docs", icon: BookOpen },
  { label: "Packages", href: "/docs/codepot-openapi", icon: Boxes },
  { label: "Guides", href: "/docs/guides", icon: BookOpen },
  { label: "Codepot Lang", href: "/docs/codepot-lang", icon: Languages },
] as const;

export function MobileSidebar({ isOpen, onClose }: MobileSidebarProps) {
  return (
    <>
      {isOpen && <div className="fixed inset-0 z-60 bg-black/50 backdrop-blur-sm lg:hidden" onClick={onClose} />}
      <div className={`fixed inset-y-0 left-0 z-70 w-72 transform border-r border-border bg-card transition-transform duration-300 ease-in-out lg:hidden motion-reduce:transition-none ${isOpen ? "translate-x-0" : "-translate-x-full"}`}>
        <div className="flex h-full flex-col">
          <div className="flex h-16 items-center justify-between border-b border-border px-4">
            <Link href="/" className="flex items-center gap-2" onClick={onClose}>
              <Image src="/logo.svg" alt="" width={42} height={42} className="h-10 w-10" />
              <span className="landing-display text-xl font-semibold tracking-tight text-foreground">Codepot</span>
            </Link>
            <button type="button" onClick={onClose} aria-label="Close navigation menu" className="rounded-md p-2 text-muted-foreground hover:bg-card-muted hover:text-foreground">
              <X className="h-5 w-5" />
            </button>
          </div>

          <nav className="flex-1 overflow-y-auto p-4">
            <div className="space-y-2">
              {links.map(({ label, href, icon: Icon }) => (
                <Link key={href} href={href} className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-foreground transition-colors hover:bg-card-muted" onClick={onClose}>
                  <Icon className="h-4 w-4 text-primary" />
                  {label}
                </Link>
              ))}
              <a href="https://github.com/alidantech-org/codepot" target="_blank" rel="noopener noreferrer" className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-foreground transition-colors hover:bg-card-muted">
                <GitHubIcon />
                GitHub
              </a>
            </div>

            <div className="mt-8 rounded-2xl border border-border bg-background/75 p-4 shadow-sm">
              <p className="font-mono text-[10px] uppercase tracking-widest text-primary">Ecosystem</p>
              <p className="mt-2 text-sm leading-6 text-muted-foreground">
                Supported prototypes feed the official JavaScript runtime and the final Rust language platform.
              </p>
              <Link href="/docs/ecosystem" className="mt-3 inline-block text-sm font-medium text-foreground hover:text-primary" onClick={onClose}>
                View ecosystem →
              </Link>
            </div>
          </nav>

          <div className="border-t border-border p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Theme</span>
              <ThemeToggle />
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
