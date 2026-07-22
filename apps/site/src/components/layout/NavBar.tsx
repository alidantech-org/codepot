"use client";

import Image from "next/image";
import Link from "next/link";
import { Code, Menu, Package, Search } from "lucide-react";
import { useState } from "react";

import { GitHubIcon } from "@/components/icons/GitHubIcon";
import { MobileSidebar } from "@/components/layout/MobileSidebar";
import { ThemeToggle } from "@/components/theme-toggle";
import { Command } from "@/components/ui/command";

export function NavBar() {
  const [searchOpen, setSearchOpen] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <>
      <MobileSidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <nav className="sticky top-0 z-50 border-b border-border bg-background/80 backdrop-blur-xl">
        <div className="mx-auto flex h-14 items-center justify-between gap-3 px-2 md:px-6">
          <div className="flex min-w-0 items-center gap-3 lg:gap-8">
            <button type="button" onClick={() => setSidebarOpen(true)} aria-label="Open navigation menu" className="inline-flex h-10 w-10 items-center justify-center rounded-xl text-muted-foreground transition-colors hover:bg-card-muted hover:text-foreground lg:hidden">
              <Menu className="h-5 w-5" />
            </button>

            <Link href="/" className="flex min-w-0 items-center gap-0.5">
              <Image src="/logo.svg" alt="Codepot logo" width={34} height={34} className="shrink-0" />
              <span className="truncate bg-linear-to-r from-primary to-secondary bg-clip-text text-lg font-bold tracking-tight text-transparent">codepot</span>
            </Link>

            <div className="hidden items-center gap-1 text-sm text-muted-foreground lg:flex">
              <Link href="/#features" className="rounded-xl px-3 py-2 transition-colors hover:bg-card-muted hover:text-foreground">Features</Link>
              <Link href="/#pipeline" className="rounded-xl px-3 py-2 transition-colors hover:bg-card-muted hover:text-foreground">How it works</Link>
              <Link href="/#examples" className="rounded-xl px-3 py-2 transition-colors hover:bg-card-muted hover:text-foreground">Examples</Link>
              <Link href="/docs" className="rounded-xl px-3 py-2 transition-colors hover:bg-card-muted hover:text-foreground">Docs</Link>
            </div>
          </div>

          <div className="flex shrink-0 items-center gap-1.5 sm:gap-2">
            <ThemeToggle />
            <button type="button" onClick={() => setSearchOpen(true)} aria-label="Search documentation" className="inline-flex h-10 w-10 items-center justify-center rounded-xl text-muted-foreground transition-colors hover:bg-card-muted hover:text-foreground sm:w-auto md:border md:border-border md:bg-card md:px-3 lg:min-w-52 lg:justify-start">
              <Search className="h-4 w-4 shrink-0" />
              <span className="ml-2 hidden text-sm sm:inline">Search...</span>
            </button>

            <div className="hidden items-center gap-1 md:flex">
              <a href="https://github.com/alidantech-org/codepot" target="_blank" rel="noopener noreferrer" className="inline-flex h-10 items-center gap-2 rounded-xl border border-border bg-card px-3 text-sm text-foreground transition-colors hover:bg-card-muted"><GitHubIcon /><span className="hidden xl:inline">GitHub</span></a>
              <a href="https://www.npmjs.com/package/codepotx" target="_blank" rel="noopener noreferrer" className="inline-flex h-10 items-center gap-2 rounded-xl border border-border bg-card px-3 text-sm text-foreground transition-colors hover:bg-card-muted"><Package className="h-4 w-4" /><span className="hidden xl:inline">NPM</span></a>
              <a href="https://github.com/alidantech-org/codepot_lang" target="_blank" rel="noopener noreferrer" className="inline-flex h-10 items-center gap-2 rounded-xl border border-border bg-card px-3 text-sm text-foreground transition-colors hover:bg-card-muted"><Code className="h-4 w-4" /><span className="hidden xl:inline">Language</span></a>
            </div>
          </div>
        </div>
      </nav>

      {searchOpen && (
        <div className="fixed inset-0 z-60 bg-background/80 p-4 backdrop-blur-sm" onClick={() => setSearchOpen(false)}>
          <div className="mx-auto mt-20 w-full max-w-xl sm:mt-28" onClick={(event) => event.stopPropagation()}>
            <Command className="overflow-hidden rounded-2xl border border-border bg-card shadow-2xl">
              <div className="flex items-center border-b border-border px-4">
                <Search className="mr-3 h-4 w-4 shrink-0 text-muted-foreground" />
                <input placeholder="Search documentation..." className="h-12 w-full bg-transparent text-sm outline-none placeholder:text-muted-foreground" autoFocus />
              </div>
              <div className="max-h-[50vh] overflow-y-auto p-3">
                <Link href="/docs" onClick={() => setSearchOpen(false)} className="block rounded-xl px-4 py-3 text-sm text-muted-foreground transition-colors hover:bg-card-muted hover:text-foreground">Browse Codepot documentation</Link>
              </div>
            </Command>
          </div>
        </div>
      )}
    </>
  );
}
