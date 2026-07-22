"use client";

import Link from "next/link";
import { Code, Package, X } from "lucide-react";

import { GitHubIcon } from "@/components/icons/GitHubIcon";
import { ThemeToggle } from "@/components/theme-toggle";

interface MobileSidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export function MobileSidebar({ isOpen, onClose }: MobileSidebarProps) {
  return (
    <>
      {isOpen && <div className="fixed inset-0 z-60 bg-black/50 lg:hidden" onClick={onClose} />}
      <div className={`fixed inset-y-0 left-0 z-70 w-64 transform border-r border-border bg-card transition-transform duration-300 ease-in-out lg:hidden ${isOpen ? "translate-x-0" : "-translate-x-full"}`}>
        <div className="flex h-full flex-col">
          <div className="flex items-center justify-between border-b border-border p-4">
            <Link href="/" className="flex items-center gap-2.5" onClick={onClose}>
              <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-linear-to-br from-primary to-secondary font-mono text-[11px] font-medium text-white">cp</span>
              <span className="bg-linear-to-r from-primary to-secondary bg-clip-text text-xl font-bold tracking-tight text-transparent">codepot</span>
            </Link>
            <button type="button" onClick={onClose} aria-label="Close navigation menu" className="rounded-md p-2 text-muted-foreground hover:bg-card-muted hover:text-foreground">
              <X className="h-5 w-5" />
            </button>
          </div>

          <nav className="flex-1 overflow-y-auto p-4">
            <div className="space-y-2">
              <Link href="/#features" className="block rounded-md px-3 py-2 text-sm font-medium text-foreground hover:bg-card-muted" onClick={onClose}>Features</Link>
              <Link href="/#pipeline" className="block rounded-md px-3 py-2 text-sm font-medium text-foreground hover:bg-card-muted" onClick={onClose}>How it works</Link>
              <Link href="/#examples" className="block rounded-md px-3 py-2 text-sm font-medium text-foreground hover:bg-card-muted" onClick={onClose}>Examples</Link>
              <Link href="/docs" className="block rounded-md px-3 py-2 text-sm font-medium text-foreground hover:bg-card-muted" onClick={onClose}>Documentation</Link>
            </div>

            <div className="mt-8 space-y-2">
              <div className="px-3 py-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">Links</div>
              <a href="https://github.com/alidantech-org/codepot" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 rounded-md px-3 py-2 text-sm text-foreground hover:bg-card-muted"><GitHubIcon />GitHub</a>
              <a href="https://www.npmjs.com/package/codepotx" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 rounded-md px-3 py-2 text-sm text-foreground hover:bg-card-muted"><Package className="h-4 w-4" />NPM</a>
              <a href="https://github.com/alidantech-org/codepot_lang" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 rounded-md px-3 py-2 text-sm text-foreground hover:bg-card-muted"><Code className="h-4 w-4" />Codepot Lang</a>
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
