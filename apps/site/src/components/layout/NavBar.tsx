"use client";

import Image from "next/image";
import Link from "next/link";
import { Menu, Search } from "lucide-react";
import { useMemo, useState } from "react";

import { GitHubIcon } from "@/components/icons/GitHubIcon";
import { MobileSidebar } from "@/components/layout/MobileSidebar";
import { ThemeToggle } from "@/components/theme-toggle";
import { Command } from "@/components/ui/command";
import { DOC_INDEX } from "@/generated/docs";
import Logo from "./Logo";

const primaryLinks = [
  { label: "Docs", href: "/docs" },
  { label: "Packages", href: "/docs/codepot-openapi" },
  { label: "Guides", href: "/docs/guides" },
  { label: "Codepot Lang", href: "/docs/codepot-lang" },
] as const;

export function NavBar() {
  const [searchOpen, setSearchOpen] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [query, setQuery] = useState("");
  const results = useMemo(() => {
    const value = query.trim().toLowerCase();
    if (!value) return DOC_INDEX.slice(0, 6);
    return DOC_INDEX.filter((item) => item.searchText.includes(value)).slice(
      0,
      8,
    );
  }, [query]);

  function closeSearch() {
    setSearchOpen(false);
    setQuery("");
  }

  return (
    <>
      <MobileSidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <nav className="sticky top-0 z-20 border-b border-border bg-background/82 backdrop-blur-xl">
        <div className="mx-auto flex h-15 items-center justify-between gap-3 px-2 md:px-6">
          <div className="flex min-w-0 items-center gap-3 lg:gap-8">
            <button
              type="button"
              onClick={() => setSidebarOpen(true)}
              aria-label="Open navigation menu"
              className="inline-flex h-10 w-10 items-center justify-center rounded-xl text-muted-foreground transition-colors hover:bg-card-muted hover:text-foreground lg:hidden"
            >
              <Menu className="h-5 w-5" />
            </button>

            <Logo />

            <div className="hidden items-center gap-1 text-sm text-muted-foreground lg:flex">
              {primaryLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className="rounded-xl px-3 py-2 transition-colors hover:bg-card-muted hover:text-foreground"
                >
                  {link.label}
                </Link>
              ))}
              <a
                href="https://github.com/alidantech-org/codepot"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 rounded-xl px-3 py-2 transition-colors hover:bg-card-muted hover:text-foreground"
              >
                <GitHubIcon />
                GitHub
              </a>
            </div>
          </div>

          <div className="flex shrink-0 items-center gap-1.5 sm:gap-2">
            <ThemeToggle />
            <button
              type="button"
              onClick={() => setSearchOpen(true)}
              aria-label="Search documentation"
              className="inline-flex h-10 w-10 items-center justify-center rounded-xl text-muted-foreground transition-colors hover:bg-card-muted hover:text-foreground sm:w-auto md:border md:border-border md:bg-card/80 md:px-3 lg:min-w-52 lg:justify-start"
            >
              <Search className="h-4 w-4 shrink-0" />
              <span className="ml-2 hidden text-sm sm:inline">Search docs</span>
            </button>
          </div>
        </div>
      </nav>

      {searchOpen && (
        <div
          className="fixed inset-0 z-60 bg-background/80 p-4 backdrop-blur-sm"
          onClick={closeSearch}
        >
          <div
            className="mx-auto mt-20 w-full max-w-xl sm:mt-28"
            onClick={(event) => event.stopPropagation()}
          >
            <Command className="overflow-hidden rounded-2xl border border-border bg-card shadow-2xl">
              <div className="flex items-center border-b border-border px-4">
                <Search className="mr-3 h-4 w-4 shrink-0 text-muted-foreground" />
                <input
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  onKeyDown={(event) => {
                    if (event.key === "Escape") closeSearch();
                  }}
                  placeholder="Search all Codepot documentation..."
                  className="h-12 w-full bg-transparent text-sm outline-none placeholder:text-muted-foreground"
                  autoFocus
                />
              </div>
              <div className="max-h-[50vh] overflow-y-auto p-3 scrollbar-thin">
                {results.length ? (
                  results.map((item) => (
                    <Link
                      key={item.slug}
                      href={`/docs/${item.slug}`}
                      onClick={closeSearch}
                      className="block rounded-xl px-4 py-3 transition-colors hover:bg-card-muted"
                    >
                      <span className="block text-sm font-medium text-foreground">
                        {item.title}
                      </span>
                      <span className="mt-1 block text-xs text-muted-foreground">
                        {item.section}
                        {item.description ? ` · ${item.description}` : ""}
                      </span>
                    </Link>
                  ))
                ) : (
                  <div className="rounded-xl px-4 py-3 text-sm text-muted-foreground">
                    No documentation matches “{query}”.
                  </div>
                )}
              </div>
            </Command>
          </div>
        </div>
      )}
    </>
  );
}
